import streamlit as st
import requests

st.set_page_config(page_title="Freight Pricing Demo", layout="centered")
st.title("🌍 Freight Pricing Calculator")

# List of common ports
ports = [
    "Shanghai", "Singapore", "Rotterdam", "Dubai", "Los Angeles", "Hamburg", "Mumbai", "Hong Kong", "Antwerp", "Busan", "New York", "Jebel Ali", "Port Klang", "Felixstowe", "Colombo"
]
port_of_loading = st.selectbox("Select Port of Loading:", ports)
port_of_destination = st.selectbox("Select Port of Destination:", ports)

usd_amount = st.number_input("Enter Freight Cost (USD):", min_value=0.0, step=10.0)
margin = st.slider("Add Margin (%)", 0, 20, 5)

if st.button("Calculate in INR"):
    try:
        response = requests.get(
            f"https://api.exchangerate-api.com/v4/latest/USD"
        ).json()
        rate = response["rates"]["INR"]
        final_price = usd_amount * rate * (1 + margin / 100)
        st.success(f"💰 Final Freight Price: ₹{final_price:,.2f}")
        st.caption(f"Exchange Rate: 1 USD = ₹{rate}")
        st.caption(f"Port of Loading: {port_of_loading}")
        st.caption(f"Port of Destination: {port_of_destination}")
    except Exception as e:
        st.error("Error fetching exchange rate. Please try again later.")
