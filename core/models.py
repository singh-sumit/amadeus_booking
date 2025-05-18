from pydantic import BaseModel, constr, conint
from typing import Optional

class FlightSearchRequest(BaseModel):
    from_location: constr(min_length=3, max_length=3)
    to_location: constr(min_length=3, max_length=3)
    departure_date: str  # ISO format "YYYY-MM-DD"
    num_passengers: conint(gt=0)
    seat_class: str  # e.g., "Economy", "Premium Economy", etc.

# Optional: For later use to display flight options
class FlightOption(BaseModel):
    airline: str
    flight_number: str
    departure_time: str
    arrival_time: str
    price: float
    seat_class: str
