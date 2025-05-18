import os
# from dotenv import load_dotenv

# load_dotenv() 

AMADEUS_CLIENT_ID =os.environ.get("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET =os.environ.get("AMADEUS_CLIENT_SECRET")
AMADEUS_ENVIRONMENT =os.environ.get("AMADEUS_ENVIRONMENT", "test") # test or production

REDIS_URL =os.environ.get("REDIS_URL", "redis://localhost:6379")
