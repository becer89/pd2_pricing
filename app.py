import streamlit as st
import pandas as pd
import re

# 📌 Title of the application
st.set_page_config(page_title="PD2 Pricing App", layout="wide")
st.title("💰 PD2 Pricing App")
st.markdown("Upload your Excel file and calculate item prices.")

# 🎨 Custom CSS for better UI
st.markdown("""
    <style>
        .stSlider { padding-top: 20px; }
        .stButton>button { width: 100%; }
        .css-1aumxhk { font-size: 20px; font-weight: bold; }
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

    # 🔹 Add prices to item names
    df['Display Name'] = df.apply(lambda row: f"{row['Name']} [HR: {row['HR Min']:.2f}-{row['HR Max']:.2f}, "
                                              f"Gul: {row['GUL Min']:.2f}-{row['GUL Max']:.2f}, "
                                              f"WSS: {row['WSS Min']:.2f}-{row['WSS Max']:.2f}]", axis=1)

    # 🎛️ User input interface
    st.subheader("🛍️ Select item quantities:")
    user_inputs = {}

    with st.expander("Select Items", expanded=True):
        for index, row in df.iterrows():
            unique_key = f"{row['Name']}_{index}"
            user_inputs[row['Name']] = st.slider(
                row['Display Name'], min_value=0, max_value=50, step=1, key=unique_key
            )

    # 🧮 Calculate total prices
    if st.button("🧾 Calculate Value"):
        total_hr_min = sum(user_inputs.get(name, 0) * row['HR Min'] for name, row in df.set_index('Name').iterrows())
        total_hr_max = sum(user_inputs.get(name, 0) * row['HR Max'] for name, row in df.set_index('Name').iterrows())
        total_gul_min = sum(user_inputs.get(name, 0) * row['GUL Min'] for name, row in df.set_index('Name').iterrows())
        total_gul_max = sum(user_inputs.get(name, 0) * row['GUL Max'] for name, row in df.set_index('Name').iterrows())
        total_wss_min = sum(user_inputs.get(name, 0) * row['WSS Min'] for name, row in df.set_index('Name').iterrows())
        total_wss_max = sum(user_inputs.get(name, 0) * row['WSS Max'] for name, row in df.set_index('Name').iterrows())

        # 📊 Display results in a table
        st.subheader("📊 Summary")
        results_df = pd.DataFrame({
            "Currency": ["HR", "Gul", "WSS"],
            "Min Value": [total_hr_min, total_gul_min, total_wss_min],
            "Max Value": [total_hr_max, total_gul_max, total_wss_max]
        })

        st.table(results_df)
