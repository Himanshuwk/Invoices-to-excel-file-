import streamlit as st
import io
import re
import pandas as pd
from google.cloud import vision
from google.oauth2 import service_account

# Load GCP credentials
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = vision.ImageAnnotatorClient(credentials=creds)

st.title("📄 Invoice to Excel Converter")

# File uploader
uploaded_files = st.file_uploader("Upload Invoices (Images/PDFs)", 
                                  type=["jpg", "jpeg", "png", "pdf"], 
                                  accept_multiple_files=True)

def extract_text(file):
    content = file.read()
    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)
    text = response.full_text_annotation.text
    return text

def parse_invoice(text):
    """Very simple regex-based parsing — you can expand rules based on your data."""
    sales = []
    purchase = []
    gst = []
    companies = []

    # Example dummy rules (adjust to your invoices)
    for line in text.split("\n"):
        line = line.strip()
        if "sale" in line.lower():
            sales.append({"Description": line})
        if "purchase" in line.lower():
            purchase.append({"Description": line})
        if "gst" in line.lower():
            gst.append({"GST Detail": line})
        if re.search(r"\bPvt Ltd\b|\bLtd\b|\bLLP\b", line):
            companies.append({"Company": line})

    return (
        pd.DataFrame(sales) if sales else pd.DataFrame(columns=["Description"]),
        pd.DataFrame(purchase) if purchase else pd.DataFrame(columns=["Description"]),
        pd.DataFrame(gst) if gst else pd.DataFrame(columns=["GST Detail"]),
        pd.DataFrame(companies) if companies else pd.DataFrame(columns=["Company"])
    )

if uploaded_files:
    all_sales, all_purchase, all_gst, all_companies = [], [], [], []

    for file in uploaded_files:
        st.write(f"📑 Processing: {file.name}")
        text = extract_text(file)
        sales, purchase, gst, companies = parse_invoice(text)

        if not sales.empty: all_sales.append(sales)
        if not purchase.empty: all_purchase.append(purchase)
        if not gst.empty: all_gst.append(gst)
        if not companies.empty: all_companies.append(companies)

    # Combine all
    df_sales = pd.concat(all_sales, ignore_index=True) if all_sales else pd.DataFrame(columns=["Description"])
    df_purchase = pd.concat(all_purchase, ignore_index=True) if all_purchase else pd.DataFrame(columns=["Description"])
    df_gst = pd.concat(all_gst, ignore_index=True) if all_gst else pd.DataFrame(columns=["GST Detail"])
    df_companies = pd.concat(all_companies, ignore_index=True) if all_companies else pd.DataFrame(columns=["Company"])

    # --- PREVIEW TABLES IN APP ---
    st.subheader("📊 Extracted Tables Preview")

    st.write("### Sales")
    st.dataframe(df_sales)

    st.write("### Purchase")
    st.dataframe(df_purchase)

    st.write("### GST")
    st.dataframe(df_gst)

    st.write("### Companies")
    st.dataframe(df_companies)

    # Save to single Excel sheet with 4 tables
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        start_row = 0
        df_sales.to_excel(writer, sheet_name="Invoices", index=False, startrow=start_row)
        start_row += len(df_sales) + 3
        df_purchase.to_excel(writer, sheet_name="Invoices", index=False, startrow=start_row)
        start_row += len(df_purchase) + 3
        df_gst.to_excel(writer, sheet_name="Invoices", index=False, startrow=start_row)
        start_row += len(df_gst) + 3
        df_companies.to_excel(writer, sheet_name="Invoices", index=False, startrow=start_row)

    st.download_button(
        label="📥 Download Excel",
        data=output.getvalue(),
        file_name="invoices.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
