import streamlit as st
import pandas as pd
import re

# 📌 Page configuration - set a narrower layout
st.set_page_config(page_title="PD2 Pricing App", layout="centered")
st.title("💰 PD2 Pricing App")
st.markdown("Upload your Excel file and calculate item prices.")

# 🎨 Custom CSS for better UI
st.markdown("""
    <style>
        .stTextInput { margin-top: -8px; } /* Reduce spacing above input */
        .stButton>button { width: 100%; padding: 10px; font-size: 18px; }
        .summary-box { 
            border: 2px solid #4CAF50; padding: 15px; border-radius: 10px; 
            background-color: #f9f9f9; text-align: center;
        }
        .summary-title { font-size: 22px; font-weight: bold; color: #4CAF50; }
        .summary-value { font-size: 18px; margin-bottom: 10px; }
        .item-container { 
            border: 1px solid #ddd; padding: 8px; border-radius: 5px; 
            margin-bottom: 5px; background-color: #f9f9f9;
        }
        .item-name { font-size: 18px; font-weight: bold; margin-bottom: -5px; } /* Reduce spacing */
        .item-price { font-size: 14px; font-style: italic; color: gray; margin-bottom: -5px; } /* Reduce spacing */
        .stNumberInput>div>div>input { width: 60px !important; } /* Make input field shorter */
    </style>
""", unsafe_allow_html=True)

# 📥 File uploader
uploaded_file = st.file_uploader("📂 Upload an Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name="Trade Values", header=1, dtype=str)
    df.dropna(how='all', inplace=True)

    # 🏷️ Merge columns for item names
    df['Name'] = df['Number'].astype(str).str.strip() + ' ' + df['Rune'].astype(str).str.strip()

    # 🗑️ Remove items "1 El" to "17 Lum"
    runes_to_remove = [
        "1 El", "2 Eld", "3 Tir", "4 Nef", "5 Eth", "6 Ith", "7 Tal", "8 Ral", "9 Ort", "10 Thul",
        "11 Amn", "12 Sol", "13 Shael", "14 Dol", "15 Hel", "16 Io", "17 Lum"
    ]
    df = df[~df['Name'].isin(runes_to_remove)]

    # 🔍 Remove numbers from "18 Ko" to "33 Zod"
    def clean_name(name):
        name = re.sub(r'\(.*?\)', '', name)  # Remove everything inside parentheses
        name = name.replace(' nan', '').strip()  # Remove "nan" artifacts
        name = re.sub(r'^(1[8-9]|2[0-9]|3[0-3])\s', '', name)  # Remove numbers
        return name

    df['Name'] = df['Name'].apply(clean_name)
    df = df[~df['Name'].isin(['nan', 'PD2 Currency Data', 'Number Rune'])]

    # 🔢 Function to process price ranges
    def parse_min_max(value):
        if isinstance(value, str):
            value = value.replace(',', '.').strip()
            if '-' in value:
                try:
                    numbers = [float(x.strip()) for x in value.split('-')]
                    return numbers[0], numbers[1]
                except ValueError:
                    return 0, 0
        try:
            num = float(value)
            return num, num
        except (ValueError, TypeError):
            return 0, 0

    df.rename(columns={'HR value': 'HR', 'GV (Gul value)': 'GUL', 'WSS value': 'WSS'}, inplace=True)
    df[['HR Min', 'HR Max']] = df['HR'].astype(str).apply(parse_min_max).apply(pd.Series)
    df[['GUL Min', 'GUL Max']] = df['GUL'].astype(str).apply(parse_min_max).apply(pd.Series)
    df[['WSS Min', 'WSS Max']] = df['WSS'].astype(str).apply(parse_min_max).apply(pd.Series)
    df.drop(columns=['HR', 'GUL', 'WSS'], inplace=True)
    df.fillna(0, inplace=True)
    df = df.drop_duplicates(subset=['Name'], keep='first')

    # 🔹 Format prices for display
    def format_price(value_min, value_max):
        value_min = f"{value_min:.2f}".rstrip('0').rstrip('.')  # Remove trailing zeros
        value_max = f"{value_max:.2f}".rstrip('0').rstrip('.')
        return f"{value_min}-{value_max}" if value_min != value_max else value_min

    df['Formatted Price'] = df.apply(lambda row: f"HR: {format_price(row['HR Min'], row['HR Max'])}, "
                                                 f"Gul: {format_price(row['GUL Min'], row['GUL Max'])}, "
                                                 f"WSS: {format_price(row['WSS Min'], row['WSS Max'])}", axis=1)

    # 🎛️ UI with two columns
    col1, col2 = st.columns([3, 1])

    # 📜 Left Column - Items List
    with col1:
        st.subheader("🛍️ Select item quantities:")
        user_inputs = {}

        for index, row in df.iterrows():
            col1a, col1b = st.columns([3, 1])  # Create row layout (name | input field)
            with col1a:
                st.markdown(f"<div class='item-container'>"
                            f"<p class='item-name'>{row['Name']}</p>"
                            f"<p class='item-price'>{row['Formatted Price']}</p>"
                            f"</div>", unsafe_allow_html=True)
            with col1b:
                unique_key = f"{row['Name']}_{index}"
                user_inputs[row['Name']] = st.number_input("", min_value=0, step=1, key=unique_key)

    # 📊 Right Column - Summary
    with col2:
        st.subheader("📊 Summary")

        if st.button("🧾 Calculate Value"):
            total_hr_min = sum(user_inputs.get(name, 0) * row['HR Min'] for name, row in df.set_index('Name').iterrows())
            total_hr_max = sum(user_inputs.get(name, 0) * row['HR Max'] for name, row in df.set_index('Name').iterrows())
            total_gul_min = sum(user_inputs.get(name, 0) * row['GUL Min'] for name, row in df.set_index('Name').iterrows())
            total_gul_max = sum(user_inputs.get(name, 0) * row['GUL Max'] for name, row in df.set_index('Name').iterrows())
            total_wss_min = sum(user_inputs.get(name, 0) * row['WSS Min'] for name, row in df.set_index('Name').iterrows())
            total_wss_max = sum(user_inputs.get(name, 0) * row['WSS Max'] for name, row in df.set_index('Name').iterrows())

            # 📊 Styled summary box
            st.markdown(f"""
                <div class='summary-box'>
                    <p class='summary-title'>🧾 Total Value</p>
                    <p class='summary-value'><strong>HR:</strong> {format_price(total_hr_min, total_hr_max)}</p>
                    <p class='summary-value'><strong>Gul:</strong> {format_price(total_gul_min, total_gul_max)}</p>
                    <p class='summary-value'><strong>WSS:</strong> {format_price(total_wss_min, total_wss_max)}</p>
                </div>
            """, unsafe_allow_html=True)
