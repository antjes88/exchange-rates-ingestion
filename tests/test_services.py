import os
from typing import Tuple, List

from src import services, model, destination_repository, source_repository


def test_source_exchange_rates(
    repository_with_exchange_rates: Tuple[
        destination_repository.BigQueryDestinationRepository,
        List[model.ExchangeRate],
    ],
    fake_ecb_api: Tuple[
        source_repository.EcbApiCallerFake,
        List[model.ExchangeRate],
        List[model.CurrencyPair],
    ],
):
    """
    GIVEN a fake ecb api
    WHEN we call the service source_exchange_rates()
    THEN the fake data sourced from the fake api should be loaded into the data repository
    """
    fake_ecb_api_caller, expected_exchange_rates, currency_pairs = fake_ecb_api
    bq_repository, EXCHANGE_RATES = repository_with_exchange_rates
    services.source_exchange_rates(bq_repository, currency_pairs, fake_ecb_api_caller)

    expected_exchange_rates = expected_exchange_rates + EXCHANGE_RATES

    query_job = bq_repository.client.query(
        f"SELECT * FROM {os.environ['DATASET']}.{os.environ['DESTINATION_TABLE']}"
    )
    rows = query_job.result()
    results_exchange_rates = []
    for row in rows:
        results_exchange_rates.append(
            model.ExchangeRate(
                date=row.date,
                exchange_rate=row.exchange_rate,
                currency_pair=model.CurrencyPair(row.base_currency, row.quote_currency),
                source=row.source,
            )
        )

    assert len(expected_exchange_rates) == len(results_exchange_rates)
    for exchange_rate in expected_exchange_rates:
        assert exchange_rate in results_exchange_rates
