from fastapi import FastAPI
from utils import get_usd_inr_rate, calculate_pricing

app = FastAPI(title="Freight Pricing API")

@app.get("/")
def root():
    return {"message": "Freight Pricing API is running"}

@app.get("/convert/")
def convert(usd_amount: float):
    rate = get_usd_inr_rate()
    return {
        "usd": usd_amount,
        "usd_inr_rate": rate,
        "inr_value": round(usd_amount * rate, 2)
    }

@app.get("/calculate/")
def calculate(base_freight_usd: float, margin_percent: float = 5):
    rate = get_usd_inr_rate()
    final_price = calculate_pricing(base_freight_usd, rate, margin_percent)
    return {
        "base_freight_usd": base_freight_usd,
        "usd_inr_rate": rate,
        "margin_percent": margin_percent,
        "final_price_inr": round(final_price, 2)
    }
          