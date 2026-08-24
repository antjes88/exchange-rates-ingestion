import click
from src.entrypoints.cli.get_ecb_rates import get_ecb_rates
import warnings
from dotenv import load_dotenv

warnings.filterwarnings("ignore", category=UserWarning)


@click.group()
def cli():
    pass


cli.add_command(get_ecb_rates)

if __name__ == "__main__":
    load_dotenv(dotenv_path=".env", override=True)
    cli()
