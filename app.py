import streamlit as st
import pandas as pd
import io
from google.oauth2 import service_account
from google.cloud import vision

# Authenticate with Google Cloud using Streamlit secrets
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = vision.ImageAnnotatorClient(credentials=creds)

st.title("📊 Invoice to Excel Converter")
st.write("Upload your Sales and Purchase invoice images to generate an Excel report.")

# ---- File Uploaders ----
st.subheader("Upload Sales Invoices")
sales_files = st.file_uploader(
    "Upload Sales Invoice Images",
    type=["jpg", "jpeg", "png", "pdf"],
    accept_multiple_files=True
)

st.subheader("Upload Purchase Invoices")
purchase_files = st.file_uploader(
    "Upload Purchase Invoice Images",
    type=["jpg", "jpeg", "png", "pdf"],
    accept_multiple_files=True
)

# ---- OCR Extraction Function ----
def extract_text_from_image(image_file):
    content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    if texts:
        return texts[0].description
    return ""

# ---- Data Processing Functions ----
def process_sales_invoices(files):
    sales_data = []
    for file in files:
        text = extract_text_from_image(file)
        # 📝 Simplified example: You will add your own parsing logic here
        sales_data.append({
            "Invoice_No": "INV001",
            "Company": "ABC Traders",
            "GSTIN": "22AAAAA0000A1Z5",
            "Net_2.5%": 1000,
            "CGST_2.5%": 25,
            "SGST_2.5%": 25,
            "Net_6%": 0,
            "CGST_6%": 0,
            "SGST_6%": 0,
            "Net_9%": 0,
            "CGST_9%": 0,
            "SGST_9%": 0,
            "Net_14%": 0,
            "CGST_14%": 0,
            "SGST_14%": 0,
            "Total_Quantity": 10,
            "HSN_Codes": "1001, 1002"
        })
    return pd.DataFrame(sales_data)

def process_purchase_invoices(files):
    purchase_data = []
    for file in files:
        text = extract_text_from_image(file)
        # 📝 Simplified example: You will add your own parsing logic here
        purchase_data.append({
            "Invoice_No": "PINV001",
            "Company": "XYZ Suppliers",
            "GSTIN": "27BBBBB1111B2Z6",
            "Net_2.5%": 500,
            "CGST_2.5%": 12.5,
            "SGST_2.5%": 12.5,
            "Net_6%": 0,
            "CGST_6%": 0,
            "SGST_6%": 0,
            "Net_9%": 0,
            "CGST_9%": 0,
            "SGST_9%": 0,
            "Net_14%": 0,
            "CGST_14%": 0,
            "SGST_14%": 0
        })
    return pd.DataFrame(purchase_data)

# ---- Generate Excel ----
if st.button("Generate Excel"):
    if not sales_files and not purchase_files:
        st.error("Please upload at least one sales or purchase invoice.")
    else:
        sales_df = process_sales_invoices(sales_files) if sales_files else pd.DataFrame()
        purchase_df = process_purchase_invoices(purchase_files) if purchase_files else pd.DataFrame()

        # Net GST Calculation
        net_gst = {}
        for col in ["CGST_2.5%", "SGST_2.5%", "CGST_6%", "SGST_6%", "CGST_9%", "SGST_9%", "CGST_14%", "SGST_14%"]:
            net_gst[col] = sales_df[col].sum() - purchase_df[col].sum() if not sales_df.empty and not purchase_df.empty else 0
        net_gst_df = pd.DataFrame([net_gst])

        # Company List
        company_list = pd.concat([sales_df[["Company", "GSTIN"]], purchase_df[["Company", "GSTIN"]]], ignore_index=True).drop_duplicates()

        # Save to Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            sales_df.to_excel(writer, sheet_name="Invoices", startrow=0, index=False)
            purchase_df.to_excel(writer, sheet_name="Invoices", startrow=len(sales_df)+3, index=False)
            net_gst_df.to_excel(writer, sheet_name="Invoices", startrow=len(sales_df)+len(purchase_df)+6, index=False)
            company_list.to_excel(writer, sheet_name="Invoices", startrow=len(sales_df)+len(purchase_df)+10, index=False)

        st.success("Excel file generated successfully!")
        st.download_button(
            label="📥 Download Excel",
            data=output.getvalue(),
            file_name="invoices_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
