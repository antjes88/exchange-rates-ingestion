import datetime as dt
from abc import ABC, abstractmethod
from google.cloud import bigquery
from typing import List
from src import model


class AbstractDestinationRepository(ABC):

    @abstractmethod
    def load_exchange_rates(self, exchange_rates: List[model.ExchangeRate]) -> None:

        raise NotImplementedError


class BigQueryDestinationRepository(AbstractDestinationRepository):

    def __init__(self, client: bigquery.Client):
        self.client = client
        self.exchange_rates_destination = "raw.exchange_rates"

    def load_exchange_rates(self, exchange_rates: List[model.ExchangeRate]) -> None:

        dictify = [
            {
                "date": exchange_rate.date.strftime("%Y-%m-%d"),
                "exchange_rate": exchange_rate.exchange_rate,
                "base_currency": exchange_rate.currency_pair.base,
                "quote_currency": exchange_rate.currency_pair.quote,
                "source": exchange_rate.source,
                "creation_date": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            for exchange_rate in exchange_rates
        ]
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        )
        load_job = self.client.load_table_from_json(
            dictify, self.exchange_rates_destination, job_config=job_config
        )
        load_job.result()
