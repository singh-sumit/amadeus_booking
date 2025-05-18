# worker.py (or celery_worker.py)
import os
import logging
import time
from amadeus import Client, ResponseError

from celery_worker import celery
from core.models import FlightSearchRequest
from core.config import AMADEUS_CLIENT_ID, AMADEUS_CLIENT_SECRET

# Setup Amadeus client
amadeus = Client(client_id=AMADEUS_CLIENT_ID, client_secret=AMADEUS_CLIENT_SECRET)

TRAVELER_INFO = [
    {
        "id": "1",
        "dateOfBirth": "1997-01-01",
        "name": {"firstName": "SUMIT", "lastName": "SINGH"},
        "gender": "MALE",
        "contact": {
            "emailAddress": "sumit@example.com",
            "phones": [
                {
                    "deviceType": "MOBILE",
                    "countryCallingCode": "977",
                    "number": "9812345678",
                }
            ],
        },
        "documents": [
            {
                "documentType": "PASSPORT",
                "number": "123456789",
                "expiryDate": "2030-12-31",
                "issuanceCountry": "NP",
                "nationality": "NP",
                "holder": True,
            }
        ],
    }
]

CONTACT_INFO = [
    {
        "addresseeName": {"firstName": "PABLO", "lastName": "RODRIGUEZ"},
        "companyName": "INCREIBLE VIAJES",
        "purpose": "STANDARD",
        "phones": [
            {
                "deviceType": "LANDLINE",
                "countryCallingCode": "34",
                "number": "480080071",
            },
            {"deviceType": "MOBILE", "countryCallingCode": "33", "number": "480080072"},
        ],
        "emailAddress": "support@increibleviajes.es",
        "address": {
            "lines": ["Calle Prado, 16"],
            "postalCode": "28014",
            "cityName": "Madrid",
            "countryCode": "ES",
        },
    }
]


@celery.task(name="worker.echo_task")
def echo_task(message):
    print(f"Echo task received message: {message}")
    return message


@celery.task(bind=True, name="worker.search_and_hold_flight")
def search_and_hold_flight(self, search_data: dict):
    search_request = FlightSearchRequest(**search_data)
    logging.info(f"Starting flight search for {search_request}")

    max_attempts = 1
    delay_seconds = 10

    for attempt in range(1, max_attempts + 1):
        try:
            logging.info(f"Attempt {attempt} to search flights via Amadeus...")
            response = amadeus.shopping.flight_offers_search.get(
                originLocationCode=search_request.from_location,
                destinationLocationCode=search_request.to_location,
                departureDate=search_request.departure_date,
                adults=search_request.num_passengers,
                travelClass=search_request.seat_class.upper(),  # ECONOMY, BUSINESS etc.
                # nonStop=True,
                currencyCode="USD",
                max=5,
            )

            offers = response.data

            if not offers:
                logging.info("No flights found, retrying after delay...")
                time.sleep(delay_seconds)
                continue

            selected_offer = offers[0]
            # get flight offer price
            offer_price_response = amadeus.shopping.flight_offers.pricing.post(
                selected_offer
            )
            # Create a hold using Amadeus booking API
            flight_offer_price_data = offer_price_response.data["flightOffers"][0]
            print("## flight_offer_price_data", flight_offer_price_data)
            booking_response = hold_flight_offer(flight_offer_price_data)
            print(
                "## booking response",
                booking_response,
            )

            if "error" in booking_response:
                print("## got error", dir(booking_response))
                return {
                    "status": "hold_failed",
                    "offers": offers,
                    "error": booking_response["error"],
                }

            hold_reference = f"AMADEUS_HOLD_{self.request.id}"

            # todo: create hold request for selected_offer using amadeus

            result = {
                "status": "held",
                "offers": offers,
                "hold_details": booking_response,
            }

            logging.info(f"Flight held: {result}")
            return result

        except ResponseError as err:
            logging.error(f"Amadeus error: {err}")
            time.sleep(delay_seconds)
        except Exception as ex:
            logging.exception("Unexpected error during flight search")
            time.sleep(delay_seconds)

    # Final fallback
    result = {"status": "not_found"}
    return result


def hold_flight_offer(flight_offer_price_data: dict):
    """
    Uses Amadeus Flight Orders API to simulate hold with delayed ticketing.
    """
    try:
        response = amadeus.post(
            "/v1/booking/flight-orders",
            {
                "data": {
                    "type": "flight-order",
                    "flightOffers": [flight_offer_price_data],
                    "travelers": [
                        {
                            "id": "1",
                            "dateOfBirth": "1982-01-16",
                            "name": {"firstName": "JORGE", "lastName": "GONZALES"},
                            "gender": "MALE",
                            "contact": {
                                "emailAddress": "jorge.gonzales833@telefonica.es",
                                "phones": [
                                    {
                                        "deviceType": "MOBILE",
                                        "countryCallingCode": "34",
                                        "number": "480080076",
                                    }
                                ],
                            },
                            "documents": [
                                {
                                    "documentType": "PASSPORT",
                                    "birthPlace": "Madrid",
                                    "issuanceLocation": "Madrid",
                                    "issuanceDate": "2015-04-14",
                                    "number": "00000000",
                                    "expiryDate": "2025-06-14",
                                    "issuanceCountry": "ES",
                                    "validityCountry": "ES",
                                    "nationality": "ES",
                                    "holder": True,
                                }
                            ],
                        },
                        {
                            "id": "2",
                            "dateOfBirth": "2012-10-11",
                            "gender": "FEMALE",
                            "contact": {
                                "emailAddress": "jorge.gonzales833@telefonica.es",
                                "phones": [
                                    {
                                        "deviceType": "MOBILE",
                                        "countryCallingCode": "34",
                                        "number": "480080076",
                                    }
                                ],
                            },
                            "name": {"firstName": "ADRIANA", "lastName": "GONZALES"},
                        },
                    ],
                    "remarks": {
                        "general": [
                            {
                                "subType": "GENERAL_MISCELLANEOUS",
                                "text": "ONLINE BOOKING FROM INCREIBLE VIAJES",
                            }
                        ]
                    },
                    "ticketingAgreement": {"option": "DELAY_TO_CANCEL", "delay": "6D"},
                    "contacts": [
                        {
                            "addresseeName": {
                                "firstName": "PABLO",
                                "lastName": "RODRIGUEZ",
                            },
                            "companyName": "INCREIBLE VIAJES",
                            "purpose": "STANDARD",
                            "phones": [
                                {
                                    "deviceType": "LANDLINE",
                                    "countryCallingCode": "34",
                                    "number": "480080071",
                                },
                                {
                                    "deviceType": "MOBILE",
                                    "countryCallingCode": "33",
                                    "number": "480080072",
                                },
                            ],
                            "emailAddress": "support@increibleviajes.es",
                            "address": {
                                "lines": ["Calle Prado, 16"],
                                "postalCode": "28014",
                                "cityName": "Madrid",
                                "countryCode": "ES",
                            },
                        }
                    ],
                }
            },
        )
        # response = amadeus.booking.flight_orders.post(flight_offer, TRAVELER_INFO)
        print("### status", dir(response))
        return response.data
    except ResponseError as e:
        logging.error(f"Failed to hold flight: {e}")
        raise e
