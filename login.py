import os
import boto3
import redis
from playwright.sync_api import sync_playwright

DYNAMO_TABLE = os.environ.get("DYNAMO_TABLE", "creds")
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
TOKEN_TTL_SECONDS = 45 * 60  # 45 minutes

dynamodb = boto3.resource('dynamodb')
creds_table = dynamodb.Table(DYNAMO_TABLE)
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

def get_token(vendor_id):
    """
    Retrieve an authentication token for the given vendor.
    Checks Redis cache first; if not found or expired, performs login.
    1. Construct a Redis key for this vendor's token
    2. Check Redis for an existing token
    3. Optionally, we could verify token validity by a test request here
    4. No valid cached token, proceed to login
    5. Perform login using Playwright to get a new token
    6. Store the token in Redis cache with expiry
    """
    token_key = f"oocl:token:{vendor_id}"
    cached_token = redis_client.get(token_key)
    if cached_token:
        try:
            token_str = cached_token.decode('utf-8')
        except AttributeError:
            token_str = cached_token  # already a str if Redis is configured differently
        return token_str

    creds = _fetch_credentials(vendor_id)
    if not creds:
        raise Exception(f"No credentials found for vendorID {vendor_id}")

    username = creds.get('username')
    password = creds.get('password')
    if not username or not password:
        raise Exception(f"Incomplete credentials for vendorID {vendor_id}")

    token = _perform_login(username, password)
    if not token:
        raise Exception("Login failed: token not obtained")

    redis_client.set(token_key, token, ex=TOKEN_TTL_SECONDS)
    return token

def _fetch_credentials(vendor_id):
    try:
        response = creds_table.get_item(Key={'vendorID': vendor_id})
    except Exception as e:
        raise Exception(f"Error accessing DynamoDB: {e}")
    item = response.get('Item')
    if not item:
        return None
    return item

"""
    Use Playwright to log in to FreightSmart and return the session token.
"""
def _perform_login(username, password):
    login_url = "https://freightsmart.oocl.com/app/login?loginType=OOCL"
    token_value = None
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context()
        page = context.new_page()
        try:
            page.goto(login_url, timeout=60000)  # 60-second timeout  
            page.wait_for_selector("input", timeout=10000)
            filled = False
            for selector in ['input[name="username"]', 'input[name="email"]', 'input[type="text"]']:
                if not filled:
                    try:
                        page.fill(selector, username)
                        filled = True
                    except Exception:
                        continue
            if not filled:
                raise Exception("Username field not found on login page")
            filled = False
            for selector in ['input[name="password"]', 'input[type="password"]']:
                if not filled:
                    try:
                        page.fill(selector, password)
                        filled = True
                    except Exception:
                        continue
            if not filled:
                raise Exception("Password field not found on login page")
            try:
                page.click("button:has-text(\"Sign In\")")
            except Exception:
                page.keyboard.press("Enter")
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception as e:
            browser.close()
            raise Exception(f"Login page interaction failed: {e}")
        cookies = context.cookies()
        for cookie in cookies:
            if cookie.get("name") == "token":
                token_value = cookie.get("value")
                break
        browser.close()

    return token_value
