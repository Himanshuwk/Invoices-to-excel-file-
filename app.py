import streamlit as st
import pandas as pd
from google.cloud import vision
from google.oauth2 import service_account

# Load Google Vision credentials
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = vision.ImageAnnotatorClient(credentials=creds)

st.title("GST Invoice Analyzer 📊")

# Upload Sales & Purchase Invoices
sales_files = st.file_uploader("Upload Sales Invoices", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
purchase_files = st.file_uploader("Upload Purchase Invoices", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if st.button("Process Invoices"):
    st.write("🔍 Extracting data... (Vision API)")

    # Placeholder DataFrames for now
    sales_df = pd.DataFrame(columns=["Invoice No", "Date", "Company Name", "GSTIN", 
                                     "Net Sales 2.5%", "CGST 2.5%", "SGST 2.5%",
                                     "Net Sales 6%", "CGST 6%", "SGST 6%",
                                     "Net Sales 9%", "CGST 9%", "SGST 9%",
                                     "Net Sales 14%", "CGST 14%", "SGST 14%",
                                     "Total Quantity", "HSN Codes"])

    purchase_df = pd.DataFrame(columns=["Invoice No", "Date", "Company Name", "GSTIN", 
                                        "Net Purchase 2.5%", "CGST 2.5%", "SGST 2.5%",
                                        "Net Purchase 6%", "CGST 6%", "SGST 6%",
                                        "Net Purchase 9%", "CGST 9%", "SGST 9%",
                                        "Net Purchase 14%", "CGST 14%", "SGST 14%"])

    gst_summary = pd.DataFrame(columns=["GST Slab", "Total Sales GST", "Total Purchase GST", "Net GST Payable"])
    company_master = pd.DataFrame(columns=["Company Name", "GSTIN"])

    with pd.ExcelWriter("gst_report.xlsx", engine="openpyxl") as writer:
        sales_df.to_excel(writer, sheet_name="GST_Report", startrow=0, index=False)
        purchase_df.to_excel(writer, sheet_name="GST_Report", startrow=len(sales_df)+3, index=False)
        gst_summary.to_excel(writer, sheet_name="GST_Report", startrow=len(sales_df)+len(purchase_df)+6, index=False)
        company_master.to_excel(writer, sheet_name="GST_Report", startrow=len(sales_df)+len(purchase_df)+len(gst_summary)+9, index=False)

    st.success("✅ Report generated!")
    with open("gst_report.xlsx", "rb") as f:
        st.download_button("Download Excel Report", f, file_name="gst_report.xlsx")

