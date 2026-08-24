from typing import Tuple, List
import os
from src import model, destination_repository


def test_load_exchange_rates(
    repository_with_exchange_rates: Tuple[
        destination_repository.BigQueryDestinationRepository,
        List[model.ExchangeRate],
    ],
):
    """
    GIVEN a repository and a collection of Exchange Rates
    WHEN they are passed as arguments to BiqQueryRepository.load_exchange_rates()
    THEN Exchange Rates should be loaded into the destination table in the data repository
    """
    bq_repository, EXCHANGE_RATES = repository_with_exchange_rates
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

    assert len(EXCHANGE_RATES) == len(results_exchange_rates)
    for exchange_rate in EXCHANGE_RATES:
        assert exchange_rate in results_exchange_rates
