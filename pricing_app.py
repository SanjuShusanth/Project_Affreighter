import streamlit as st
import requests
from fpdf import FPDF
import io
import base64
from pathlib import Path

# Read and encode image as base64

st.set_page_config(page_title="Affreighter Pricing Demo", layout="wide")

img_path = Path("image/customs.jpg")
if img_path.exists():
    with open(img_path, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image:
                linear-gradient(rgba(255,255,255,0.5), rgba(255,255,255,0.5)),
                url('data:image/jpg;base64,{img_base64}');
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
            background-color: rgba(0,0,0,0) !important;
        }}
        /* Bright color for field labels */
        label, .stTextInput label, .stNumberInput label, .stSelectbox label {{
            color: #000000 !important; /* Gold/bright yellow */
        }}
        /* Bright color for markdown text */
        .markdown-text-container, .markdown-text-container * {{
            color: #000000 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.error("Background image not found. Please check the 'image/customs.jpg' path.")

# Page content
st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: black; font-weight: bold;'>🌍 Affreighter Logistics Pricing Calculator</h1>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: black;'>
<h3 style='color: black;'>Welcome to the Freight Pricing Calculator</h3>
<p style='max-width: 600px; margin: auto; color: black;'>
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
col1, col2, col3 = st.columns(3)
with col1:
    port_of_loading = st.selectbox("Select Port of Loading:", ports)
with col2:
    port_of_destination = st.selectbox("Select Port of Destination:", ports)
with col3:
    # Only the info icon above the select field
    incoterm_expenses = {
        "EXW": "EXW (Ex Works): Buyer pays all costs from seller's premises, including freight, insurance, customs, and delivery.",
        "FOB": "FOB (Free On Board): Seller pays for transport to port and loading. Buyer pays ocean/air freight, insurance, and destination charges.",
        "CIF": "CIF (Cost, Insurance, Freight): Seller pays for transport, insurance, and freight to destination port. Buyer pays import duties and local delivery.",
        "DAP": "DAP (Delivered At Place): Seller pays all costs up to named place of destination, excluding import duties/taxes.",
        "DDP": "DDP (Delivered Duty Paid): Seller pays all costs including import duties/taxes, up to buyer's door. Buyer pays nothing extra."
    }
    st.markdown("<span style='font-weight: 500;'>Select Shipment Terms (Incoterms): <span style='font-size: 18px; color: #007bff;'>&#9432;</span></span>", unsafe_allow_html=True)
    shipment_terms = st.selectbox("", incoterms)

col4, col5, col6 = st.columns(3)
with col4:
    Dimensions_of_Cartons = st.text_input("Enter Dimensions of Cartons (LxWxH in cm):", "40x30x20")
with col5:
    No_of_Cartons = st.number_input("Enter Number of Cartons:", min_value=1, step=1)
with col6:
    Gross_Weight = st.number_input("Enter Gross Weight(kg):", min_value=0.1, step=0.1)

col7, col8, col9 = st.columns(3)
with col7:
    Shipment_mode = st.selectbox("Select Shipment Mode:", ["Airline", "Ocean"])
with col8:
    usd_amount = st.number_input("Enter Freight Cost (USD):", min_value=0.0, step=10.0)
with col9:
    EXW_origin_charges = st.number_input("EXW + Origin Charges (including CFS & LSS) (USD):", min_value=0.0, step=10.0)

# Weight per CBM field (only for Ocean)
if Shipment_mode == "Ocean":
    weight_per_cbm = st.number_input("Enter Weight per CBM (kg):", min_value=500, value=1000, step=50)
else:
    weight_per_cbm = None

# Separate row for margin
margin = st.slider("Add Margin (%)", 0, 20, 5)

# Chargeable Weight Calculation
length, width, height = [float(x) for x in Dimensions_of_Cartons.split('x')]
cbm = (length * width * height * No_of_Cartons) / 1_000_000  # CBM calculation
chargeable_weight = None
chargeable_weight_info = ""

if Shipment_mode == "Ocean":
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

if st.button("Calculate in INR"):
    pdf_output = None
    try:
        response = requests.get(
            f"https://api.exchangerate-api.com/v4/latest/USD"
        ).json()
        rate = response["rates"]["INR"]
        total_usd = usd_amount + EXW_origin_charges
        final_price = total_usd * rate * (1 + margin / 100)
        st.markdown(f"<span style='color:black; font-weight:bold;'>💰 Total Cost (Freight + EXW Charges): ₹{final_price:,.2f}</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:black;'>Exchange Rate: 1 USD = ₹{rate}</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:black;'>Port of Loading: {port_of_loading}</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:black;'>Port of Destination: {port_of_destination}</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:black;'>Shipment Terms: {shipment_terms}</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:black;'>Number of Cartons: {No_of_Cartons}</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:black;'>Dimensions of Cartons: {Dimensions_of_Cartons} cm</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:black;'>Gross Weight: {Gross_Weight} kg</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:black;'>Shipment Mode: {Shipment_mode}</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:black;'>CBM: {cbm:.3f}</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:black;'>Chargeable Weight: {chargeable_weight:.2f} kg</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:black;'>{chargeable_weight_info}</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:black;'>EXW + Origin Charges (including CFS & LSS): ${EXW_origin_charges:,.2f}</span>", unsafe_allow_html=True)

        # PDF generation
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Affreighter Pricing Calculator Result", ln=True, align='C')
            pdf.ln(10)
            pdf.cell(0, 10, txt=f"Total Cost (Freight + EXW Charges) (INR): {final_price:,.2f} INR", ln=True)
            pdf.cell(0, 10, txt=f"Exchange Rate: 1 USD = {rate} INR", ln=True)
            pdf.cell(0, 10, txt=f"Port of Loading: {port_of_loading}", ln=True)
            pdf.cell(0, 10, txt=f"Port of Destination: {port_of_destination}", ln=True)
            pdf.cell(0, 10, txt=f"Shipment Terms: {shipment_terms}", ln=True)
            pdf.cell(0, 10, txt=f"Number of Cartons: {No_of_Cartons}", ln=True)
            pdf.cell(0, 10, txt=f"Dimensions of Cartons: {Dimensions_of_Cartons} cm", ln=True)
            pdf.cell(0, 10, txt=f"Gross Weight: {Gross_Weight} kg", ln=True)
            pdf.cell(0, 10, txt=f"Shipment Mode: {Shipment_mode}", ln=True)
            pdf.cell(0, 10, txt=f"CBM: {cbm:.3f}", ln=True)
            pdf.cell(0, 10, txt=f"Chargeable Weight: {chargeable_weight:.2f} kg", ln=True)
            pdf.cell(0, 10, txt=f"{chargeable_weight_info}", ln=True)
            pdf.cell(0, 10, txt=f"EXW + Origin Charges (including CFS & LSS): ${EXW_origin_charges:,.2f}", ln=True)
            pdf_output = io.BytesIO(pdf.output(dest='S').encode('latin1'))
        except Exception as pdf_error:
            st.error(f"PDF generation failed: {pdf_error}")
    except Exception as e:
        st.error("Error fetching exchange rate. Please try again later.")
    if pdf_output:
        st.download_button(
            label="Download PDF",
            data=pdf_output,
            file_name="freight_pricing_result.pdf",
            mime="application/pdf"
        )
st.markdown('</div>', unsafe_allow_html=True)
