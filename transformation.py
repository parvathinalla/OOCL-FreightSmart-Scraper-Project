from bs4 import BeautifulSoup
import re

def format_results(html_content):
    """
    Parse the HTML content of the FreightSmart results page and format it into structured JSON.
    Returns a dictionary with the parsed quote data.
    Attempt to find quote entries. Possible strategies:
    1. Each quote might be contained in a <label> (if quotes are selectable) or in a <tr> or <div>.
    2. We look for elements containing price information (e.g., "USD" followed by numbers).
    3. Use known labels like 'Free Time' or 'Transit Time' to extract those details.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    quotes = []

    quote_elements = []

    for lbl in soup.find_all('label'):
        text = lbl.get_text()
        if "USD" in text:
            quote_elements.append(text)
    if not quote_elements:
        for row in soup.find_all('tr'):
            text = row.get_text()
            if "USD" in text:
                quote_elements.append(text)
    if not quote_elements:
        for div in soup.find_all('div'):
            text = div.get_text()
            if "USD" in text:
                if text.count("USD") == 1:
                    quote_elements.append(text)

    for quote_text in quote_elements:
        quote_data = {}
        price_match = re.search(r'([A-Z]{3})\s*([\d,]+\.?\d*)', quote_text)   
        if price_match:
            currency = price_match.group(1)
            amount_str = price_match.group(2).replace(',', '')
            try:
                price_value = float(amount_str)
            except ValueError:
                price_value = amount_str  # If it contains something like "1200.00", float will handle; otherwise keep as string
            quote_data["currency"] = currency
            quote_data["price"] = price_value

        free_match = re.search(r'Free Time\s*[:\-]?\s*(\d+)\s*day', quote_text, flags=re.IGNORECASE)
        if free_match:
            quote_data["free_time_days"] = int(free_match.group(1))

        transit_match = re.search(r'Transit Time\s*[:\-]?\s*(\d+)\s*day', quote_text, flags=re.IGNORECASE)
        if transit_match:
            quote_data["transit_time_days"] = int(transit_match.group(1))

        if "E-Spot" in quote_text:
            quote_data["product"] = "E-Spot"
        elif "Secured" in quote_text:
            quote_data["product"] = "Secured E-Quote"
        elif "E-Quote" in quote_text:
            quote_data["product"] = "E-Quote"

        if "price" in quote_data:
            quotes.append(quote_data)

    result = {
        "origin": None,
        "destination": None,
        "container_type": None,
        "cargo_ready_date": None,
        "quotes": quotes
    }
    return result
