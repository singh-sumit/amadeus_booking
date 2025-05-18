# streamlit_app/display.py
# Contains functions to render data, such as flight results tables
# and hold summary information, in the Streamlit UI.

import streamlit as st
import pandas as pd
from datetime import datetime

def format_duration(duration_str):
    """Formats ISO 8601 duration string (e.g., PT16H25M) to a more readable format (e.g., 16H 25M)."""
    if not duration_str or not duration_str.startswith("PT"):
        return "N/A"
    return duration_str.replace("PT", "").replace("H", "H ").replace("M", "M").strip()

    
def render_results_table(offers):
    """
    Renders flight search results as a table.
    """
    print("### Result", offers)
    if not offers:
        st.warning("No flight data found or the data is in an unexpected format.")
        return

    if not isinstance(offers, list):
        st.error("❌ Invalid data: Flight offers must be provided as a list.")
        return

    if not offers:
        st.info("ℹ️ No flight offers to display.")
        return

    processed_offers = []
    for i, offer in enumerate(offers):
        try:
            # Ensure offer is a dictionary
            if not isinstance(offer, dict):
                st.warning(f"Skipping item at index {i}: Not a valid dictionary.")
                continue

            # --- Basic Offer Info ---
            offer_id = offer.get("id", f"N/A_{i+1}")

            # --- Itinerary Details ---
            itineraries = offer.get("itineraries", [])
            if not itineraries or not isinstance(itineraries, list) or not itineraries[0]:
                st.warning(f"Offer {offer_id}: Missing or invalid itinerary data. Skipping.")
                continue
            
            primary_itinerary = itineraries[0]
            segments = primary_itinerary.get("segments", [])
            if not segments or not isinstance(segments, list):
                st.warning(f"Offer {offer_id}: Itinerary has no segments. Skipping.")
                continue

            # Route: From first segment's departure to last segment's arrival
            route_parts = [seg.get("departure", {}).get("iataCode", "N/A") for seg in segments]
            route_parts.append(segments[-1].get("arrival", {}).get("iataCode", "N/A"))
            # Filter out "N/A" if a code was missing, unless it's the only one
            route_parts_filtered = [code for code in route_parts if code != "N/A"]
            if not route_parts_filtered and route_parts: # if all were N/A, show the original N/A list
                 route_display = " → ".join(route_parts)
            elif not route_parts_filtered: # if no segments at all
                 route_display = "N/A"
            else:
                 route_display = " → ".join(route_parts_filtered)


            # Departure and Arrival Times
            first_segment_departure = segments[0].get("departure", {}).get("at")
            last_segment_arrival = segments[-1].get("arrival", {}).get("at")

            departure_display = "N/A"
            if first_segment_departure:
                try:
                    dep_dt = datetime.fromisoformat(first_segment_departure.replace("Z", "+00:00"))
                    departure_display = dep_dt.strftime('%Y-%m-%d %H:%M %Z')
                except ValueError:
                    departure_display = first_segment_departure # Fallback to raw string

            arrival_display = "N/A"
            if last_segment_arrival:
                try:
                    arr_dt = datetime.fromisoformat(last_segment_arrival.replace("Z", "+00:00"))
                    arrival_display = arr_dt.strftime('%Y-%m-%d %H:%M %Z')
                except ValueError:
                    arrival_display = last_segment_arrival # Fallback to raw string
            
            total_duration = format_duration(primary_itinerary.get("duration", "N/A"))
            num_stops = len(segments) - 1

            # --- Airline & Cabin ---
            # Validating airline is a good summary. For more detail, one could list all operating carriers.
            validating_airlines = offer.get("validatingAirlineCodes", ["N/A"])
            airline_display = ", ".join(validating_airlines) if validating_airlines else "N/A"

            # Traveler Pricing Details (assuming one traveler, first segment's cabin as representative)
            traveler_pricings = offer.get("travelerPricings", [])
            cabin_class = "N/A"
            checked_baggage_display = "N/A"

            if traveler_pricings and isinstance(traveler_pricings, list) and traveler_pricings[0]:
                fare_details_list = traveler_pricings[0].get("fareDetailsBySegment", [])
                if fare_details_list and isinstance(fare_details_list, list) and fare_details_list[0]:
                    first_segment_fare_details = fare_details_list[0]
                    cabin_class = first_segment_fare_details.get("cabin", "N/A").replace("_", " ").title()
                    
                    # Baggage Info
                    included_bags = first_segment_fare_details.get("includedCheckedBags", {})
                    if "quantity" in included_bags:
                        checked_baggage_display = f"{included_bags['quantity']} pc(s)"
                    elif "weight" in included_bags and "weightUnit" in included_bags:
                        checked_baggage_display = f"{included_bags['weight']} {included_bags['weightUnit']}"
                    elif not included_bags: # If includedCheckedBags key exists but is empty dict
                        checked_baggage_display = "0 pc(s)" # Or "Check airline"

            # --- Price ---
            price_info = offer.get("price", {})
            grand_total = price_info.get("grandTotal", "N/A")
            currency = price_info.get("currency", "")
            price_display = f"{grand_total} {currency}".strip() if grand_total != "N/A" else "N/A"

            processed_offers.append({
                "Offer ID": offer_id,
                "Route": route_display,
                "Departure": departure_display,
                "Arrival": arrival_display,
                "Duration": total_duration,
                "Stops": num_stops,
                "Airline(s)": airline_display,
                "Cabin": cabin_class,
                "Checked Bags": checked_baggage_display,
                "Price": price_display
            })

        except Exception as e:
            st.error(f"🚨 Error processing offer {offer.get('id', 'N/A')}: {e}")
            # Optionally log the full offer causing issues for debugging
            # st.json(offer) 

    if processed_offers:
        df = pd.DataFrame(processed_offers)
        
        # Define column order for better presentation
        column_order = [
            "Offer ID", "Route", "Departure", "Arrival", "Duration", 
            "Stops", "Airline(s)", "Cabin", "Checked Bags", "Price"
        ]
        # Ensure all columns in order exist in df, add missing ones with N/A if necessary
        for col in column_order:
            if col not in df.columns:
                df[col] = "N/A" # Or pd.NA
        
        st.dataframe(df[column_order], use_container_width=True, hide_index=True)
    elif offers: # If there was input data but nothing could be processed
        st.warning("⚠️ No flight offers could be successfully processed from the provided data.")


def render_hold_summary():
    """
    Renders the summary of the flight hold details.
    Retrieves hold information from the session state.
    """
    # Retrieve task_id and hold data from session state
    # task_id = st.session_state.get("task_id") # Not directly used here but good for context
    hold_details = st.session_state.get("hold")

    if hold_details and isinstance(hold_details, dict) and hold_details: # Check if dict and not empty
        st.subheader("Booking Hold Confirmed:") # More descriptive subheader
        # Display the hold details. st.json is good for arbitrary dicts.
        # For a more structured display, access keys directly.
        st.json(hold_details)

        # Example of more structured display if you know the keys:
        # if "confirmation_id" in hold_details:
        #     st.metric("Confirmation ID", hold_details["confirmation_id"])
        # if "price" in hold_details and "currency" in hold_details:
        #     st.metric("Total Price", f"{hold_details['price']} {hold_details['currency']}")
        # ... and so on for other relevant details
    else:
        st.info("No hold details available yet. Complete a search and select a flight to place a hold.")
