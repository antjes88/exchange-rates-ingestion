from abc import ABC, abstractmethod
from xml.etree import ElementTree as Et
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests as req
import requests_mock
import datetime as dt
from typing import List

from src import model


class AbstractSourceRepository(ABC):

    @abstractmethod
    def get_exchange_rates(
        self, currency_pairs: List[model.CurrencyPair]
    ) -> list[model.ExchangeRate]:

        raise NotImplementedError


class EcbApiCaller(AbstractSourceRepository):

    def __init__(self, days_to_register: int = 10):
        self.days_to_register = days_to_register

    def _call_to_ecb_api_exchange_rate(
        self, currency_pair: model.CurrencyPair
    ) -> req.models.Response:

        session = req.Session()
        retry = Retry(
            total=3, status_forcelist=[429, 500, 502, 504], backoff_factor=0.1
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)

        ecb_url = (
            f"https://data-api.ecb.europa.eu/service/data/EXR/"
            f"D.{currency_pair.quote}.{currency_pair.base}.SP00.A"
            f"?startPeriod=%s&endPeriod=%s"
        )
        date_from = str(
            dt.datetime.date(dt.datetime.now()) - dt.timedelta(self.days_to_register)
        )
        date_to = str(dt.datetime.date(dt.datetime.now()))

        return session.get(ecb_url % (date_from, date_to))

    @staticmethod
    def _xml_to_ecb_rates(
        response: req.models.Response, currency_pair: model.CurrencyPair
    ) -> list[model.ExchangeRate]:

        exchange_rates = []
        root = Et.fromstring(response.text)
        for series in root.iter(
            "{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Series"
        ):
            for obs, value in zip(
                series.iter(
                    "{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Obs"
                ),
                series.iter(
                    "{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Value"
                ),
            ):
                date, exchange_rate = None, None
                for child in obs.iter():
                    if "ObsDimension" in child.tag:
                        date = dt.datetime.strptime(
                            child.attrib["value"], "%Y-%m-%d"
                        ).date()
                    elif "ObsValue" in child.tag:
                        exchange_rate = float(child.attrib["value"])

                if date and exchange_rate:
                    exchange_rates.append(
                        model.ExchangeRate(
                            date=date,
                            exchange_rate=exchange_rate,
                            currency_pair=currency_pair,
                            source="ECB API",
                        )
                    )

        return exchange_rates

    def get_exchange_rates(
        self, currency_pairs: List[model.CurrencyPair]
    ) -> list[model.ExchangeRate]:

        for currency_pair in currency_pairs:
            if currency_pair.base != "EUR":
                raise ValueError(
                    "Base currency must be EUR for ECP API. "
                    "Please use the correct currency pair."
                )

        exchange_rates = []
        for currency_pair in currency_pairs:
            response = self._call_to_ecb_api_exchange_rate(currency_pair)

            if response.status_code != 200:
                raise ValueError(
                    f"ECB API returned status code {response.status_code} for currency pair {currency_pair}"
                )

            for exchange_rate in self._xml_to_ecb_rates(response, currency_pair):
                exchange_rates.append(exchange_rate)

        return exchange_rates


class EcbApiCallerFake(EcbApiCaller):

    def __init__(self, api_responses: dict[str, str], days_to_register: int = 10):
        super().__init__(days_to_register=days_to_register)
        self.api_responses = api_responses

    def _call_to_ecb_api_exchange_rate(
        self, currency_pair: model.CurrencyPair
    ) -> req.models.Response:

        url = "https://data-api.ecb.europa.eu"
        if currency_pair.quote not in self.api_responses.keys():
            with requests_mock.Mocker() as mocker:
                mocker.get(url, text="not valid", status_code=404)
                response = req.get(url)
        else:
            with open(self.api_responses[currency_pair.quote], "r") as f:
                response_text = f.read()
            with requests_mock.Mocker() as mocker:
                mocker.get(url, text=response_text, status_code=200)
                response = req.get(url)

        return response
