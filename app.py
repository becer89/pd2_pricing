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

    # 🔍 Clean item names by removing text in parentheses
    def clean_name(name):
        name = re.sub(r'\(.*?\)', '', name)  # Remove everything inside parentheses
        name = name.replace(' nan', '').strip()  # Remove "nan" artifacts
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
