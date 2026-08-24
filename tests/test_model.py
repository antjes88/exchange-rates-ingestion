from src import model
import datetime as dt
import pytest


@pytest.mark.parametrize(
    "date_left, date_right, exchange_rate_left, exchange_rate_right"
    ", currency_pair_left, currency_pair_right, source_left, source_right",
    [
        (
            dt.datetime(2021, 10, 10),
            dt.datetime(1990, 10, 10),
            0.1,
            0.1,
            model.CurrencyPair("GBP", "USD"),
            model.CurrencyPair("GBP", "USD"),
            "test",
            "test",
        ),
        (
            dt.datetime(1990, 10, 10),
            dt.datetime(1990, 10, 10),
            0.1,
            0.2,
            model.CurrencyPair("GBP", "USD"),
            model.CurrencyPair("GBP", "USD"),
            "test",
            "test",
        ),
        (
            dt.datetime(1990, 10, 10),
            dt.datetime(1990, 10, 10),
            0.2,
            0.2,
            model.CurrencyPair("GBP", "USD"),
            model.CurrencyPair("GBP", "EUR"),
            "test",
            "test",
        ),
        (
            dt.datetime(1990, 10, 10),
            dt.datetime(1990, 10, 10),
            0.2,
            0.2,
            model.CurrencyPair("GBP", "USD"),
            model.CurrencyPair("GBP", "USD"),
            "test",
            "another",
        ),
    ],
)
def test_exchange_rate_inequality(
    date_left: dt.datetime,
    date_right: dt.datetime,
    exchange_rate_left: float,
    exchange_rate_right: float,
    currency_pair_left: model.CurrencyPair,
    currency_pair_right: model.CurrencyPair,
    source_left: str,
    source_right: str,
):
    """
    GIVEN 2 exchange rates with different: date, exchange_rate,
      from_currency, to_currency and source
    WHEN they are checked for equality
    THEN the result should be that exchange rates are NOT equal
    """

    assert model.ExchangeRate(
        date=date_left,
        exchange_rate=exchange_rate_left,
        currency_pair=currency_pair_left,
        source=source_left,
    ) != model.ExchangeRate(
        date=date_right,
        exchange_rate=exchange_rate_right,
        currency_pair=currency_pair_right,
        source=source_right,
    )


@pytest.mark.parametrize("value", [1, "string", 0.1, dt.datetime.now()])
def test_exchange_rate_inequality_other(value):
    """
    GIVEN an exchange rates and another data structure
    WHEN they are checked for equality
    THEN the result should be that exchange rates are NOT equal
    """
    assert (
        model.ExchangeRate(
            date=dt.datetime.now(),
            exchange_rate=0.1,
            currency_pair=model.CurrencyPair("GBP", "USD"),
            source="test",
        )
        != value
    )


@pytest.mark.parametrize(
    "base, quote, should_raise",
    [
        ("USD", "EUR", False),
        ("GBP", "USD", False),
        ("USD", "USD", True),
        ("Usd", "eur", False),
        ("GbP", "USd", False),
    ],
)
def test_currency_pair_initialization(base: str, quote: str, should_raise: bool):
    """
    GIVEN base and quote currencies
    WHEN a CurrencyPair is initialized
    THEN it should raise a ValueError if base and quote are the same,
            otherwise it should initialize successfully
    """
    if should_raise:
        with pytest.raises(ValueError):
            model.CurrencyPair(base, quote)
    else:
        currency_pair = model.CurrencyPair(base, quote)
        assert currency_pair.base == base.upper()
        assert currency_pair.quote == quote.upper()


def test_currency_pair_equality():
    """
    GIVEN two CurrencyPair instances with the same base and quote currencies
    WHEN they are compared for equality
    THEN they should be equal
    """
    pair1 = model.CurrencyPair("USD", "EUR")
    pair2 = model.CurrencyPair("USD", "EUR")
    assert pair1 == pair2


def test_currency_pair_inequality():
    """
    GIVEN two CurrencyPair instances with different base or quote currencies
    WHEN they are compared for equality
    THEN they should not be equal
    """
    pair1 = model.CurrencyPair("USD", "EUR")
    pair2 = model.CurrencyPair("GBP", "USD")
    assert pair1 != pair2


def test_currency_pair_string_representation():
    """
    GIVEN a CurrencyPair instance
    WHEN it is converted to a string
    THEN it should return the string representation in the format 'base/quote'
    """
    pair = model.CurrencyPair("USD", "EUR")
    assert str(pair) == "USD/EUR"
