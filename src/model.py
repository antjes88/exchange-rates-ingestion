from dataclasses import dataclass, field
import datetime as dt


@dataclass(frozen=True)
class CurrencyPair:

    base: str
    quote: str

    def __post_init__(self):
        object.__setattr__(self, "base", self.base.upper())
        object.__setattr__(self, "quote", self.quote.upper())
        if self.base == self.quote:
            raise ValueError("Base and quote currencies must be different.")

    def __str__(self):
        return f"{self.base}/{self.quote}"


@dataclass(frozen=True)
class ExchangeRate:

    date: dt.date
    exchange_rate: float
    currency_pair: CurrencyPair
    source: str

    def __eq__(self, other) -> bool:
        if not isinstance(other, ExchangeRate):
            return False
        return (
            self.date == other.date
            and self.exchange_rate == other.exchange_rate
            and self.currency_pair == other.currency_pair
            and self.source == other.source
        )
