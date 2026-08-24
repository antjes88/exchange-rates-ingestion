from src import source_repository, destination_repository, services, model
from src.utils.gcp_clients import create_bigquery_client
from src.utils.logs import default_module_logger

logger = default_module_logger(__file__)


def function_entry_point(event, context):
    """
    Entry point function for ingesting ECB exchange rates into raw layer of the DW in BigQuery.
    This function initializes a BigQueryRepository and an EcbApiCaller, then calls a service to fetch and load ECB
    exchange rates into BigQuery.

    Args:
         event: The dictionary with data specific to this type of event. The `@type` field maps to
                `type.googleapis.com/google.pubsub.v1.PubsubMessage`. The `data` field maps to the PubsubMessage data
                in a base64-encoded string. The `attributes` field maps to the PubsubMessage attributes
                if any is present.
         context: Metadata of triggering event including `event_id` which maps to the PubsubMessage
                  messageId, `timestamp` which maps to the PubsubMessage publishTime, `event_type` which maps to
                  `google.pubsub.topic.publish`, and `resource` which is a dictionary that describes the service
                  API endpoint pubsub.googleapis.com, the triggering topic's name, and the triggering event type
                  `type.googleapis.com/google.pubsub.v1.PubsubMessage`.
    """

    client = create_bigquery_client()
    bq_repository = destination_repository.BigQueryDestinationRepository(client)
    days = 10
    ecb_api_caller = source_repository.EcbApiCaller(days)
    currency_pairs = [
        model.CurrencyPair("EUR", "GBP"),
        model.CurrencyPair("EUR", "USD"),
    ]
    logger.info(f"Currency pairs to load:")
    for currency_pair in currency_pairs:
        logger.info(f"'{currency_pair}'.")
    logger.info(f"Number of days to register: {days}.")

    services.source_exchange_rates(bq_repository, currency_pairs, ecb_api_caller)

    logger.info("Process completed successfully!!!")
