# OOCL-FreightSmart-Scraper-Project
This project is a Python-based web scraper that automates the OOCL FreightSmart platform to retrieve instant freight quotes. It uses Playwright for browser automation, AWS DynamoDB for securely storing login credentials, and Redis for caching session tokens.

**Authentication & Caching**: The scraper first checks a Redis cache for a recent session token. If a valid token exists (within 45 minutes of generation), it reuses it to skip the login step. Otherwise, it retrieves the user’s credentials (email and password) from a DynamoDB table (creds) using a given vendorID, performs a login on the FreightSmart website via Playwright, extracts the session token from the browser cookies, and stores this token in Redis with a 45-minute expiration
freightsmart.oocl.com
. This token represents the authenticated session.

**Quote Search:** Once logged in (or a cached token is obtained), the scraper navigates to the FreightSmart quote page and inputs the shipment details: origin, destination, cargo ready date, and container type. These inputs correspond to FreightSmart’s search requirements (origin, destination, container, and departure date)
freightsmart.oocl.com
. Using Playwright, the script fills out the search form and triggers the search functionality.

**Data Extraction:** After the search results load, the script scrapes the quote information from the page. This typically includes the total freight rate (with currency), and may also include other details like free time, transit time, and product type (e.g., E-Spot or E-Quote). The scraping logic is designed to parse the results into a structured format.

**Result Transformation:** The raw scraped data is then parsed and formatted into a structured JSON output. Each quote is represented as a JSON object with key details (such as price, currency, free time, etc.), making it easy to consume programmatically.
The project is organized into modular components for clarity and maintainability:

**Project Structure**
main.py: Orchestrates the overall flow. It accepts input parameters (either via user prompt or AWS Lambda event), calls the login and search modules, and returns the final JSON result.
login.py: Handles authentication. It manages DynamoDB credential retrieval, checks/sets the Redis cache for session tokens, and performs the actual login via Playwright if needed.
search.py: Uses the authenticated session to navigate the FreightSmart site and perform the quote search based on provided parameters. It then scrapes the resulting quote data from the page.
transformation.py: Parses the raw data obtained by search.py and formats it into a structured JSON (as Python dict) for output.
