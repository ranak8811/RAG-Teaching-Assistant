import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi

# Load env from project root and server/.env explicitly so running from different
# working directories still picks up the same Mongo settings.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SERVER_ENV = PROJECT_ROOT / "server" / ".env"
ROOT_ENV = PROJECT_ROOT / ".env"
load_dotenv(ROOT_ENV)
load_dotenv(SERVER_ENV)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "test_db")

if not MONGO_URI:
    raise RuntimeError(
        "MONGO_URI is not set. Add it to server/.env or .env at the project root."
    )

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000,
    tls=True,
    tlsCAFile=certifi.where(),
)
db = client[DB_NAME]

# User collection
users_collection = db["users"] 
