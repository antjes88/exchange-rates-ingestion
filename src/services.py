from src import source_repository, destination_repository, model


def source_exchange_rates(
    destination_repository: destination_repository.AbstractDestinationRepository,
    currency_pairs: list[model.CurrencyPair],
    source_repository: source_repository.AbstractSourceRepository,
) -> None:

    exchange_rates = source_repository.get_exchange_rates(currency_pairs)
    destination_repository.load_exchange_rates(exchange_rates)
