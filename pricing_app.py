import streamlit as st
import requests
from fpdf import FPDF
import io

st.set_page_config(page_title="Affreighter Pricing Demo", layout="wide")
st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>🌍 Affreighter Pricing Calculator</h1>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center;'>
<h3>Welcome to the Freight Pricing Calculator</h3>
<p style='max-width: 600px; margin: auto;'>
Easily estimate your freight costs, chargeable weights, and shipment details for global logistics.<br>
Select your ports, shipment terms, and carton details to get instant pricing in INR.<br>
This tool supports both air and ocean freight calculations, making it ideal for logistics professionals, exporters, and importers.
</p>
</p>
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
    shipment_terms = st.selectbox("Select Shipment Terms (Incoterms):", incoterms)

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
        st.success(f"💰 Total Cost (Freight + EXW Charges): ₹{final_price:,.2f}")
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
        st.caption(f"EXW + Origin Charges (including CFS & LSS): ${EXW_origin_charges:,.2f}")

        # PDF generation
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Verdana", size=12)
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
