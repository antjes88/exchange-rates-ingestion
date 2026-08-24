import pytest
import os
import datetime as dt
from typing import Generator, Tuple, List

from tests.data.ecb_exchange_rates import EXCHANGE_RATES
from src import model, destination_repository, source_repository
from src.utils.gcp_clients import create_bigquery_client


@pytest.fixture(scope="session")
def bq_repository() -> destination_repository.BigQueryDestinationRepository:

    client = create_bigquery_client(os.environ["PROJECT"])
    bq_repository = destination_repository.BigQueryDestinationRepository(client)
    bq_repository.exchange_rates_destination = (
        os.environ["DATASET"] + "." + os.environ["DESTINATION_TABLE"]
    )

    return bq_repository


@pytest.fixture(scope="function")
def repository_with_exchange_rates(
    bq_repository: destination_repository.BigQueryDestinationRepository,
) -> Generator[
    Tuple[
        destination_repository.BigQueryDestinationRepository,
        List[model.ExchangeRate],
    ],
    None,
    None,
]:

    bq_repository.load_exchange_rates(EXCHANGE_RATES)

    yield bq_repository, EXCHANGE_RATES

    bq_repository.client.delete_table(
        os.environ["DATASET"] + "." + os.environ["DESTINATION_TABLE"]
    )


@pytest.fixture(scope="function")
def fake_ecb_api() -> Tuple[
    source_repository.EcbApiCallerFake,
    List[model.ExchangeRate],
    List[model.CurrencyPair],
]:

    api_responses = {
        "GBP": "tests/data/xml_ecb_test.xml",
        "USD": "tests/data/xml_ecb_test.xml",
    }
    currency_pairs = []
    for currency_pair in api_responses.keys():
        currency_pairs.append(model.CurrencyPair("EUR", currency_pair))

    fake_ecb_api_caller = source_repository.EcbApiCallerFake(api_responses)

    expected_ecb_rates: List[model.ExchangeRate] = [
        model.ExchangeRate(
            date=dt.date(2023, 11, 6),
            exchange_rate=0.8664,
            currency_pair=model.CurrencyPair("EUR", "GBP"),
            source="ECB API",
        ),
        model.ExchangeRate(
            date=dt.date(2023, 11, 7),
            exchange_rate=0.86855,
            currency_pair=model.CurrencyPair("EUR", "GBP"),
            source="ECB API",
        ),
        model.ExchangeRate(
            date=dt.date(2023, 11, 8),
            exchange_rate=0.87015,
            currency_pair=model.CurrencyPair("EUR", "GBP"),
            source="ECB API",
        ),
        model.ExchangeRate(
            date=dt.date(2023, 11, 9),
            exchange_rate=0.87205,
            currency_pair=model.CurrencyPair("EUR", "GBP"),
            source="ECB API",
        ),
        model.ExchangeRate(
            date=dt.date(2023, 11, 10),
            exchange_rate=0.87435,
            currency_pair=model.CurrencyPair("EUR", "GBP"),
            source="ECB API",
        ),
        model.ExchangeRate(
            date=dt.date(2023, 11, 6),
            exchange_rate=0.8664,
            currency_pair=model.CurrencyPair("EUR", "USD"),
            source="ECB API",
        ),
        model.ExchangeRate(
            date=dt.date(2023, 11, 7),
            exchange_rate=0.86855,
            currency_pair=model.CurrencyPair("EUR", "USD"),
            source="ECB API",
        ),
        model.ExchangeRate(
            date=dt.date(2023, 11, 8),
            exchange_rate=0.87015,
            currency_pair=model.CurrencyPair("EUR", "USD"),
            source="ECB API",
        ),
        model.ExchangeRate(
            date=dt.date(2023, 11, 9),
            exchange_rate=0.87205,
            currency_pair=model.CurrencyPair("EUR", "USD"),
            source="ECB API",
        ),
        model.ExchangeRate(
            date=dt.date(2023, 11, 10),
            exchange_rate=0.87435,
            currency_pair=model.CurrencyPair("EUR", "USD"),
            source="ECB API",
        ),
    ]

    return fake_ecb_api_caller, expected_ecb_rates, currency_pairs
