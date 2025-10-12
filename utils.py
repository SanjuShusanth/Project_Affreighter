import requests

def get_usd_inr_rate():
    """Fetch current USD to INR conversion rate using free API."""
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url)
        data = response.json()
        return data["rates"]["INR"]
    except Exception as e:
        print("Error fetching exchange rate:", e)
        return 83.0  # fallback rate

def calculate_pricing(base_usd, conversion_rate, margin_percent):
    """Simple freight pricing logic"""
    inr_value = base_usd * conversion_rate
    margin = inr_value * (margin_percent / 100)
    return inr_value + margin
