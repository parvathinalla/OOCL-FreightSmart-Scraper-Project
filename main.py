import json
import os
from login import get_token
from search import perform_search
from transformation import format_results
"""Coordinates the login, search, and transformation to get quote data.
    1. Obtain an authenticated session token (from cache or via fresh login)
    2. Use the token to perform the quote search on FreightSmart
    3. Parse and structure the raw data into JSON-friendly format
"""
def main_flow(origin, destination, cargo_ready_date, container_type, vendor_id):
    token = get_token(vendor_id)
    raw_data = perform_search(token, origin, destination, cargo_ready_date, container_type)
    result = format_results(raw_data)
    return result

"""AWS Lambda entry point. Expects event with origin, destination, date, container_type, vendorID.
    1. Extract parameters from the event input (case-insensitive keys)
    2. Run the main flow to get results
    3. Return the result as JSON string (for API Gateway or similar integration)
"""
def handler(event, context):
    origin = event.get('origin') or event.get('Origin')
    destination = event.get('destination') or event.get('Destination')
    cargo_date = event.get('cargo_ready_date') or event.get('cargoReadyDate') or event.get('date')
    container_type = event.get('container_type') or event.get('containerType')
    vendor_id = event.get('vendorID') or event.get('vendorId') or event.get('vendorID')
    if not origin or not destination or not cargo_date or not container_type or not vendor_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing required input parameters"})
        }
    result = main_flow(origin, destination, cargo_date, container_type, vendor_id)
    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }

if __name__ == "__main__":
    origin = input("Origin: ").strip()
    destination = input("Destination: ").strip()
    cargo_date = input("Cargo Ready Date (YYYY-MM-DD): ").strip()
    container_type = input("Container Type (e.g., 40HC): ").strip()
    vendor_id = input("Vendor ID: ").strip()
    output = main_flow(origin, destination, cargo_date, container_type, vendor_id)
    print(json.dumps(output, indent=2))
