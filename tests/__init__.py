import os
import sys
from dotenv import load_dotenv

# load env vars
load_dotenv(dotenv_path="tests/.env", override=True)

# load path to get python files
sys.path.append(os.path.join(os.getcwd(), "src"))

# load sa if applicable
if os.environ.get("SA_JSON"):
    name = "sa.json"
    with open(name, "w") as f:
        f.write(os.environ.get("SA_JSON", ""))
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = name
