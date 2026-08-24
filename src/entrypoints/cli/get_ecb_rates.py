import os
import click
from typing import Tuple
from src import source_repository, destination_repository, services, model
from src.utils.gcp_clients import create_bigquery_client
from src.utils.logs import default_module_logger

logger = default_module_logger(__file__)


@click.command()
@click.option(
    "--currency",
    multiple=True,
    type=str,
    help="You can specify this option multiple times.",
)
@click.option(
    "--days",
    default=10,
    type=int,
    show_default=True,
    help="The number of days to register. Defaults to 10.",
)
def get_ecb_rates(currency: Tuple[str], days: int) -> None:
    """
    Fetches exchange rates against the EURO from the ECB (European Central Bank)
    API for the specified currencies and stores them in a BigQuery repository.

    Args:
        currency (Tuple[str]):
            A tuple of currency codes (e.g., ["USD", "GBP"]) for which exchange
            rates are to be fetched from ECB API.
        days (int):
            The number of days to register. Defaults to 10.
    """
    currency_pairs = [model.CurrencyPair("EUR", curr) for curr in currency]

    logger.info(f"Currency pairs to load:")
    for currency_pair in currency_pairs:
        logger.info(f"'{currency_pair}'.")
    logger.info(f"Number of days to register: {days}.")

    bq_repository = destination_repository.BigQueryDestinationRepository(
        create_bigquery_client(os.environ["PROJECT"])
    )
    ecb_api_caller = source_repository.EcbApiCaller(days_to_register=days)
    services.source_exchange_rates(bq_repository, currency_pairs, ecb_api_caller)

    logger.info("Process completed successfully!!!")
