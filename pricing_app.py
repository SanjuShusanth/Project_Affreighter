import streamlit as st
import requests

# Logistics-themed background image and overlay for readability
st.markdown(
    '''
    <style>
    body {
        background-image: url('https://images.unsplash.com/photo-1464983953574-0892a716854b?auto=format&fit=crop&w=1500&q=80');
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    .main-card {
        background: rgba(255,255,255,0.90);
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.12);
        padding: 2.5rem 2rem;
        margin: 3rem auto;
        max-width: 700px;
    }
    h1 {
        color: #1a4d8f;
        font-weight: bold;
        text-shadow: 1px 1px 2px #fff;
    }
    </style>
    ''', unsafe_allow_html=True
)
st.markdown('<div class="main-card">', unsafe_allow_html=True)

st.set_page_config(page_title="Freight Pricing Demo", layout="centered")
st.markdown("<h1 style='text-align: center;'>🌍 Freight Pricing Calculator</h1>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center;'>
<h3>Welcome to the Freight Pricing Calculator</h3>
<p style='max-width: 600px; margin: auto;'>
Easily estimate your freight costs, chargeable weights, and shipment details for global logistics.<br>
Select your ports, shipment terms, and carton details to get instant pricing in INR.<br>
This tool supports both air and ocean freight calculations, making it ideal for logistics professionals, exporters, and importers.
</p>
</div>
""", unsafe_allow_html=True)

    # List of common ports
ports = [
    "Shanghai", "Singapore", "Rotterdam", "Dubai", "Los Angeles", "Hamburg", "Mumbai", "Hong Kong", "Antwerp", "Busan", "New York", "Jebel Ali", "Port Klang", "Felixstowe", "Colombo"
]
incoterms = ["EXW", "FOB", "CIF", "DAP", "DDP"]
port_of_loading = st.selectbox("Select Port of Loading:", ports)
port_of_destination = st.selectbox("Select Port of Destination:", ports)
shipment_terms = st.selectbox("Select Shipment Terms (Incoterms):", incoterms)
Dimensions_of_Cartons = st.text_input("Enter Dimensions of Cartons (LxWxH in cm):", "40x30x20")
No_of_Cartons = st.number_input("Enter Number of Cartons:", min_value=1, step=1)
Gross_Weight = st.number_input("Enter Gross Weight(kg):", min_value=0.1, step=0.1)
Shipment_mode = st.selectbox("Select Shipment Mode:", ["Airline", "Ocean"])

# Chargeable Weight Calculation
length, width, height = [float(x) for x in Dimensions_of_Cartons.split('x')]
cbm = (length * width * height * No_of_Cartons) / 1_000_000  # CBM calculation
chargeable_weight = None
chargeable_weight_info = ""

if Shipment_mode == "Ocean":
    weight_per_cbm = st.number_input("Enter Weight per CBM (kg):", min_value=500, value=1000, step=50)
    ocean_chargeable_weight = cbm * weight_per_cbm
    if Gross_Weight > ocean_chargeable_weight:
        chargeable_weight = Gross_Weight
        chargeable_weight_info = "Gross weight is used for billing."
    else:
        chargeable_weight = ocean_chargeable_weight
        chargeable_weight_info = "Volume-based chargeable weight is used for billing."
elif Shipment_mode == "Airline":
    air_chargeable_weight = (length * width * height * No_of_Cartons) / 6000
    if Gross_Weight > air_chargeable_weight:
        chargeable_weight = Gross_Weight
        chargeable_weight_info = "Gross weight is used for billing."
    else:
        chargeable_weight = air_chargeable_weight
        chargeable_weight_info = "Volumetric chargeable weight is used for billing."

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
        st.caption(f"Shipment Terms: {shipment_terms}")
        st.caption(f"Number of Cartons: {No_of_Cartons}")
        st.caption(f"Dimensions of Cartons: {Dimensions_of_Cartons} cm")
        st.caption(f"Gross Weight: {Gross_Weight} kg")
        st.caption(f"Shipment Mode: {Shipment_mode}")
        st.caption(f"CBM: {cbm:.3f}")
        st.caption(f"Chargeable Weight: {chargeable_weight:.2f} kg")
        st.caption(chargeable_weight_info)
    except Exception as e:
        st.error("Error fetching exchange rate. Please try again later.")
st.markdown('</div>', unsafe_allow_html=True)
