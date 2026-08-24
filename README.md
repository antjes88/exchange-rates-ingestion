# Exchange Rates Ingestion

This repository provides a solution for fetching currency exchange rates. These exchange rates are ingested into a Data Warehouse (DW) layer, with the current implementation utilizing BigQuery as the DW and the European Central Bank (ECB) API as Source Repository. The repository includes tools, pipelines, and configurations designed to streamline the ingestion process while ensuring scalability and maintainability.

The solution is deployed using Terraform as a Google Cloud Function (2nd Gen, Python 3.12). This Cloud Function is executed on a schedule triggered by a Cloud Scheduler. Upon activation, the function processes the exchange rates from the ECB API into BigQuery. See the diagram below for an overview.

<p align="center">
    <img src="docs/images/solution_diagram.png" alt="Solution Diagram">
</p>

## Features

- **Development Environment**: Pre-configured development container for consistent setup.
- **Comprehensive Testing**: Includes unit tests and integration tests to ensure code reliability, along with test coverage reporting.
- **Pipeline Integration**: Automated pipelines to unit test python solution and deployment to GCP.

## Development environment

Recommended development environment is VSCode Dev Containers extension. The configuration and set up of this dev container is already defined in `.devcontainer/devcontainer.json` so setting up a new containerised dev environment on your machine is straight-forward.

Pre-requisites:
- docker installed on your machine and available on your `PATH`
- [Visual Studio Code](https://code.visualstudio.com/) (VSCode) installed on your machine
- [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) vscode extension installed

Steps:
- In VSCode go to `View -> Command Palette` and search for the command `>Dev Containers: Rebuild and Reopen in Container`

The first time you open the workspace within the container it'll take a few minutes to build the container, setup the virtual env and then login to gcloud. At the end of this process you will be presented with a url and asked to provide an authorization. Simply follow the url, permit the access and copy the auth code provided at the end back into to the terminal and press enter. 

### Configure Git 

For seamless Git usage in a Dev Container, create a local script at .devcontainer/git_config.sh (do not push this file to the repository) and set your GitHub account name and email:

```bash
#!/bin/bash

git config --global user.name "your github account name"
git config --global user.email "your github account email"
```

### Local Execution

Local execution is enhanced by the use of the Python library `Click`, which allows the creation of Command Line Interfaces. To execute the solution locally, run the command `exchange-rates-ingestion` in a Bash terminal inside the devcontainer. This command will display a message listing the available arguments for performing different actions. You can explore additional details and options by using the `--help` flag.

You need to provide a `.env` file at project root location with the following data:

```ini
PROJECT={name of the BigQuery GCP Project}
```

Example usage:

```bash
# Display help and available options
exchange-rates-ingestion --help
exchange-rates-ingestion get-ecb-rates --help

# Ingest exchange rates for USD and GBP over the last 10 days
exchange-rates-ingestion get-ecb-rates --currency USD --currency GBP --days 10
```

### Unit tests

To execute tests, provide a `tests/.env` file with the following data:

```ini
PROJECT={name of the test BigQuery GCP Project}
DESTINATION_TABLE={name of the testing table in BQ}
DATASET={name of the test destination dataset in BQ}
```

To run the tests, execute the following command in terminal:

```bash
python -m pytest -vv --cov --cov-report=html
```

Unit testing has been integrated into the CI/CD pipeline. A merge will not be approved unless all tests pass successfully. Additionally, a coverage report is automatically generated and provided as a comment for reference. A Service Account granted with roles `roles/bigquery.jobUser` and `roles/bigquery.dataEditor` (on the test dataset) is required. Current workflow, `.github/workflows/pytest.yaml`, is set to access GCP Project through Workload Identity Provider.

## Component Diagram

The code architecture of the Python solution is illustrated below. We adopt Onion/Clean Architecture, so ensuring that our Business Logic (Domain Model) has no dependencies. Our goal is to follow SOLID principles, promoting seamless future changes and enhancing code clarity.

The `src/entrypoints/cloud_function/main.py` file is used by the deployed solution as entrypoint, as required by GCP Cloud Functions. Locally, as described in the "Local Execution" section, code execution starts from the Python entrypoint located at `src/entrypoints/cli/__main__.py`. This entrypoint is invoked using the command `exchange-rates-ingestion` in a Bash terminal. 

Several entry points can be provided seamlessly because, following Clean Architecture principles, the `main.py` function is treated as the last detail. This ensures that none of the core solution code depends on the entry point; instead, the entry point depends on the core solution code. This design promotes flexibility and allows for the easy addition of new entry points without impacting the existing architecture. Which, in turn, means that the source is independent of the infrastructure. 

The Python entrypoint invokes one of the services found in `src/services.py`. In this case we have only the Source Exchange Rates. This service receives objects of the clients for both the destination repository and the source repository as parameters.

The services handle the execution by calling methods found in the Domain and Adapters to ensure the successful completion of the process.

<p align="center">
    <img src="docs/images/components_diagram.png" alt="Components Diagram">
</p>

The clients for data storage have been implemented following the Repository pattern. This design pattern abstracts the logic for retrieving and storing data, providing a higher-level interface to the rest of the application. By doing so, it enables the implementation of the Dependency Inversion Principle (DIP). This approach allows our Database Layer (Adapters) to depend on the Domain Model, rather than the other way around. This, in turn, facilitates the seamless use of the same Business Logic/Domain Model in another scenario with a different Infrastructure/Data Layer.

Related code can be found on `src/destination_repository.py` and `src/source_repository.py`.

<p align="center">
    <img src="docs/images/adapters_diagram.png" alt="Adapters Diagram">
</p>

In the picture above you can also find the Domain Model diagram representing the code found in `src/model.py`. Circles are value objects and rectangles are entities.

## CI/CD - Pipeline Integration
There are 2 CI/CD pipelines implemented as GitHub Actions:

1. **Pytest**: This pipeline is defined in the `.github/workflows/pytest.yaml` file. It is triggered on every pull request, which runs tests using `pytest`. It also generates a test coverage report to ensure code quality. If any test fails, the pipeline will block the merge process, ensuring that only reliable code is integrated into the main branch. Finally, the pipeline requires a test coverage threshold of >= 95% (`--cov-fail-under=95`). A Service Account granted with roles `roles/bigquery.jobUser` and `roles/bigquery.dataEditor` (on the test dataset) is required. Current workflow, `.github/workflows/pytest.yaml`, is set to access GCP Project through Workload Identity Provider.

2. **Deployment**: The deployment process is managed through two GitHub Actions workflows. The first workflow, `.github/workflows/terraform-validate.yaml`, validates the Terraform code and generates a deployment plan during a pull request, blocking merge in case of failures. The second workflow, `.github/workflows/terraform-apply.yaml`, executes after a merge to deploy the changes to Google Cloud Platform (GCP).

## Deployment implementation

The Terraform code in this repository automates the deployment of the Exchange Rate ingestion solution on Google Cloud Platform (GCP). It provisions and configures the necessary resources to ensure seamless ingestion and processing of data. 

The Terraform code automates the deployment process by managing the following components:

1. **Source Code Upload**: Uploads the source code zip file to the designated Cloud Function Source Code bucket.
2. **Cloud Function Creation**: Provisions the Cloud Function (2nd Gen, Python 3.12) that processes the exchange rates.
3. **Pub/Sub Topic**: Creates a Pub/Sub topic to which the Cloud Function is subscribed.
4. **Cloud Scheduler Job**: Configures a Cloud Scheduler job to publish a message to the Pub/Sub topic every day at 12:05 AM, ensuring the Cloud Function is executed on schedule.

### Considerations

The Terraform code is designed to be executed by the workflows defined in `.github/workflows/terraform-validate.yaml` and `.github/workflows/terraform-apply.yaml`. These workflows first package the source code into a zip file, which is then used as the source code for the Cloud Function during the Terraform execution.

If you prefer to execute the Terraform code locally, you must first run the `.github/package_cfsrc.sh`* bash script providing a temporary directory and the destination zip path. Once the zip file is created, you can proceed with running `terraform plan` or `terraform apply`, providing the path to the zip file:

```bash
# 1. Package Cloud Function source code (executed from repo root)
./.github/package_cfsrc.sh /tmp /tmp/cloud_function.zip

# 2. Plan or apply Terraform
cd terraform
terraform init
terraform plan -var="zip_file_path=/tmp/cloud_function.zip"
```

A final consideration is that the backend for this solution is configured to reside in Google Cloud Storage (GCS). If you plan to reuse this code, ensure you update the backend bucket name accordingly.

*\*This script must be executed at the repository root folder.*

### Prerequisites for Terraform Execution

Before the Terraform code can be executed, ensure the following:

1. **Cloud Function Service Account**:
    - Provide a Service Account for the Cloud Function with the following roles:
      - `roles/bigquery.jobUser`
      - `roles/bigquery.dataEditor`
      - `roles/cloudfunctions.invoker`
      - `roles/run.invoker`

2. **Terraform Execution Permissions**:
    - Either your user account or the Service Account used to run the Terraform code must have the following roles:
      - `roles/iam.serviceAccountUser` on the Service Account mentioned in the previous point.
      - `roles/cloudfunctions.admin`
      - `roles/storage.objectAdmin` on the _source code_, and _backend_ buckets.
      - `roles/storage.insightsCollectorService`
      - `roles/cloudscheduler.admin`
      - `roles/pubsub.admin`

To reuse the GitHub Actions workflows, follow these steps:

1. **Create a Workload Identity Provider (WIP):**  
   This enables keyless authentication for GitHub Actions.  
   - [Learn why this is needed](https://cloud.google.com/blog/products/identity-security/enabling-keyless-authentication-from-github-actions).  
   - [Follow these instructions](https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-google-cloud-platform).

2. **Set up Service Accounts:**  
   - Grant the Terraform Executor Service Account and the Pytest Service Account the necessary permissions as indicated above.
   - Assign the role `roles/iam.workloadIdentityUser`.
   - Set the Service Accounts as principals for the Workload Identity Provider created in step 1.

3. **Provide secrets:**
   Configure the following repository secrets in GitHub Actions:
   - **For Pytest (`pytest.yaml`):**
     - `WORKLOAD_IDENTITY_PROVIDER`
     - `SERVICE_ACCOUNT_PYTEST_EMAIL`
     - `PROJECT`
     - `DESTINATION_TABLE`
     - `DATASET`
   - **For Terraform (`terraform-validate.yaml` & `terraform-apply.yaml`):**
     - `WORKLOAD_IDENTITY_PROVIDER`
     - `SERVICE_ACCOUNT_EMAIL`