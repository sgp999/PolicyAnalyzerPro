import streamlit as st
from pypdf import PdfReader
from openai import OpenAI
import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()


# Page setup
st.set_page_config(page_title="PolicyAnalyzerPro", layout="wide")

# Clean UI
st.markdown(
    """
    <style>
        header {visibility: hidden;}
        .block-container {
            padding-top: 0rem;
            padding-bottom: 1rem;
        }
        .pa-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-top: 0rem;
            margin-bottom: 0.5rem;
        }
        .pa-logo {
            width: 58px;
            height: 58px;
            object-fit: contain;
            border-radius: 10px;
        }
        .pa-company {
            font-size: 22px;
            font-weight: 700;
            color: #1f2937;
            margin: 0;
            line-height: 1.1;
        }
        .pa-subtitle {
            font-size: 13px;
            color: #6b7280;
            margin: 2px 0 0 0;
        }
        .pa-title {
            margin-top: 0.4rem;
            margin-bottom: 1.2rem;
            font-size: 42px;
            font-weight: 800;
            color: #111827;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Branding/header setup
APP_DIR = Path(__file__).parent
PROJECT_DIR = APP_DIR.parent
LOGO_PATHS = [
    APP_DIR / "logo.png",
    APP_DIR / "logo.jpg",
    APP_DIR / "logo.jpeg",
    PROJECT_DIR / "logo.png",
    PROJECT_DIR / "logo.jpg",
    PROJECT_DIR / "logo.jpeg",
]
logo_path = next((path for path in LOGO_PATHS if path.exists()), None)

# If the logo was saved somewhere else in the project, find it automatically.
if logo_path is None:
    logo_matches = list(PROJECT_DIR.rglob("logo.png")) + list(PROJECT_DIR.rglob("logo.jpg")) + list(PROJECT_DIR.rglob("logo.jpeg"))
    logo_path = logo_matches[0] if logo_matches else None

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extract_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text


def compare_policies(text1, text2):
    prompt = f"""
You are an insurance expert.

Compare these two insurance policies and return:

1. Plan Name
2. Premium
3. Deductible
4. Out-of-pocket max
5. Key differences
6. Which is better and why

Policy 1:
{text1[:4000]}

Policy 2:
{text2[:4000]}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
    )

    return response.output[0].content[0].text


# UI
header_col_logo, header_col_text = st.columns([2, 6])

with header_col_logo:
    if logo_path:
        st.image(str(logo_path.resolve()), width=400)
    else:
        st.caption("Logo not found")

with header_col_text:
    st.markdown(
        """
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    "<h1 class='pa-title'>PolicyAnalyzerPro</h1>",
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:
    file1 = st.file_uploader("Upload Policy 1", type=["pdf"])

with col2:
    file2 = st.file_uploader("Upload Policy 2", type=["pdf"])

if st.button("Compare Policies"):
    if not file1 or not file2:
        st.warning("Please upload both PDF files.")
    else:
        with st.spinner("Extracting text..."):
            text1 = extract_text(file1)
            text2 = extract_text(file2)

        with st.spinner("Analyzing with AI..."):
            result = compare_policies(text1, text2)

        st.subheader("Policy Comparison Result")
        st.write(result)

        # Download button

        st.download_button(
            label="Download Comparison",
            data=result,
            file_name="policy_comparison.txt",
        )

# Footer contact links
st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; font-size:14px; color:#374151;">
        <a href="mailto:steve.pierog@gmail.com" style="text-decoration:none; color:#2563eb;">
            📧 steve.pierog@gmail.com
        </a>
        &nbsp; | &nbsp;
       <a href="tel:+12349019109" style="text-decoration:none; color:#2563eb;">
    📞 (234) 901-9109
       </a>
    </div>
    """,
    unsafe_allow_html=True,
)