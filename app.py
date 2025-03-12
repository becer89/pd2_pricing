import streamlit as st
import pandas as pd
import re

# 📌 Title of the application
st.title("PD2 Pricing App")
st.write("Upload your Excel file and calculate item prices.")

# 📥 File uploader
uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

if uploaded_file:
    # 📌 Read the "Trade Values" sheet
    df = pd.read_excel(uploaded_file, sheet_name="Trade Values", header=1, dtype=str)

    # 🧹 Remove empty rows
    df.dropna(how='all', inplace=True)

    # 🏷️ Merge columns to create the "Name" field
    df['Name'] = df['Number'].astype(str).str.strip() + ' ' + df['Rune'].astype(str).str.strip()

    # 🗑️ Remove products from "1 EL" to "17 LUM"
    runes_to_remove = [
        "1 EL", "2 ELD", "3 TIR", "4 NEF", "5 ETH", "6 ITH", "7 TAL", "8 RAL", "9 ORT", "10 THUL",
        "11 AMN", "12 SOL", "13 SHAEL", "14 DOL", "15 HEL", "16 IO", "17 LUM"
    ]
    df = df[~df['Name'].isin(runes_to_remove)]

    # 🔍 Clean item names by removing numbers from "18 KO" to "33 ZOD"
    def clean_name(name):
        name = re.sub(r'\(.*?\)', '', name)  # Remove everything inside parentheses
        name = name.replace(' nan', '').strip()  # Remove "nan" artifacts
        name = re.sub(r'^(1[8-9]|2[0-9]|3[0-3])\s', '', name)  # Remove numbers from "18 KO" to "33 ZOD"
        return name

    df['Name'] = df['Name'].apply(clean_name)

    # 🚨 Remove unnecessary rows
    df = df[~df['Name'].isin(['nan', 'PD2 Currency Data', 'Number Rune'])]

    # 🔢 Function to process value ranges
    def parse_min_max(value):
        if isinstance(value, str):
            value = value.replace(',', '.').strip()
            if '-' in value:
                try:
                    numbers = [float(x.strip()) for x in value.split('-')]
                    return numbers[0], numbers[1]  # Min and Max
                except ValueError:
                    return 0, 0
        try:
            num = float(value)
            return num, num
        except (ValueError, TypeError):
            return 0, 0

    # 🏷️ Rename price columns
    df.rename(columns={'HR value': 'HR', 'GV (Gul value)': 'GUL', 'WSS value': 'WSS'}, inplace=True)

    # 🔹 Process pricing values
    df[['HR Min', 'HR Max']] = df['HR'].astype(str).apply(parse_min_max).apply(pd.Series)
    df[['GUL Min', 'GUL Max']] = df['GUL'].astype(str).apply(parse_min_max).apply(pd.Series)
    df[['WSS Min', 'WSS Max']] = df['WSS'].astype(str).apply(parse_min_max).apply(pd.Series)

    # 🗑️ Remove old price columns
    df.drop(columns=['HR', 'GUL', 'WSS'], inplace=True)

    # 🏷️ Fill missing values with 0
    df.fillna(0, inplace=True)

    # 🗑️ Remove duplicate items to prevent multiple calculations
    df = df.drop_duplicates(subset=['Name'], keep='first')

    # 🔹 Add prices in square brackets to item names
    df['Name'] = df.apply(lambda row: f"{row['Name']} [HR: {row['HR Min']:.2f}-{row['HR Max']:.2f}, "
                                      f"Gul: {row['GUL Min']:.2f}-{row['GUL Max']:.2f}, "
                                      f"WSS: {row['WSS Min']:.2f}-{row['WSS Max']:.2f}]", axis=1)

    # 🎛️ User input for item quantities
    st.subheader("Select item quantities:")
    user_inputs = {}

    for index, row in df.iterrows():
        unique_key = f"{row['Name']}_{index}"  # Generate a unique key
        user_inputs[row['Name']] = st.number_input(
            row['Name'], min_value=0, step=1, key=unique_key
        )

    # 🧮 Calculate total prices
    if st.button("Calculate Value"):
        total_hr_min = sum(user_inputs.get(name, 0) * row['HR Min'] for name, row in df.set_index('Name').iterrows())
        total_hr_max = sum(user_inputs.get(name, 0) * row['HR Max'] for name, row in df.set_index('Name').iterrows())
        total_gul_min = sum(user_inputs.get(name, 0) * row['GUL Min'] for name, row in df.set_index('Name').iterrows())
        total_gul_max = sum(user_inputs.get(name, 0) * row['GUL Max'] for name, row in df.set_index('Name').iterrows())
        total_wss_min = sum(user_inputs.get(name, 0) * row['WSS Min'] for name, row in df.set_index('Name').iterrows())
        total_wss_max = sum(user_inputs.get(name, 0) * row['WSS Max'] for name, row in df.set_index('Name').iterrows())

        # 📊 Display results
        st.subheader("📊 Summary")
        st.write(f"✔️ **Total Value (HR)**: {total_hr_min:.2f} - {total_hr_max:.2f}")
        st.write(f"✔️ **Total Value (Gul)**: {total_gul_min:.2f} - {total_gul_max:.2f}")
        st.write(f"✔️ **Total Value (WSS)**: {total_wss_min:.2f} - {total_wss_max:.2f}")
