import streamlit as st

AMADEUS_CLIENT_ID = st.secrets["amadeus"]["client_id"]
AMADEUS_CLIENT_SECRET = st.secrets["amadeus"]["client_secret"]
AMADEUS_ENVIRONMENT = st.secrets["amadeus"]["environment"]

REDIS_URL = st.secrets["redis"]["url"]
