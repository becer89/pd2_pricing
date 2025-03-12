import streamlit as st
import pandas as pd
import re

# 📌 Page configuration
st.set_page_config(page_title="PD2 Pricing App", layout="wide")
st.title("💰 PD2 Pricing App")
st.markdown("Upload your Excel file and calculate item prices.")

# 🎨 Custom CSS for better UI
st.markdown("""
    <style>
        .stTextInput { margin-top: -5px; } /* Reduce spacing above input */
        .stButton>button { width: 100%; padding: 10px; font-size: 18px; }
        .summary-box { 
            border: 2px solid #4CAF50; padding: 15px; border-radius: 10px; 
            background-color: #f9f9f9; text-align: center;
        }
        .summary-title { font-size: 22px; font-weight: bold; color: #4CAF50; }
        .summary-value { font-size: 18px; margin-bottom: 10px; }
        .item-name { font-size: 18px; font-weight: bold; margin-bottom: -5px; } /* Reduce spacing */
        .item-price { font-size: 14px; font-style: italic; color: gray; margin-bottom: -5px; } /* Reduce spacing */
        .stNumberInput>div>div>input { width: 80px !important; } /* Make input field shorter */
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

    df['Formatted Price'] = df.apply(lambda row: f"[HR: {format_price(row['HR Min'], row['HR Max'])}, "
                                                 f"Gul: {format_price(row['GUL Min'], row['GUL Max'])}, "
                                                 f"WSS: {format_price(row['WSS Min'], row['WSS Max'])}]", axis=1)

    # 🎛️ UI with two columns
    col1, col2 = st.columns([3, 1])

    # 📜 Left Column - Grouped Items
    with col1:
        st.subheader("🛍️ Select item quantities:")
        user_inputs = {}

        categories = {
            "Runes": ["Ko", "Fal", "Lem", "Pul", "Um", "Mal", "Ist", "Gul", "Vex", "Ohm", "Lo", "Sur", "Ber", "Jah", "Cham", "Zod"],
            "Larzuk's Puzzles": ["Larzuk's Puzzlebox", "Larzuk's Puzzlepiece"],
            "Stocked Mats": ["50 Perfect Gems", "50 Jewel Fragments", "50 Runes (#1-#15)", "50 Craft Infusions", "50 'Map' Orbs", "50 Infused 'Map' Orbs"],
            "Corrupting": ["Worldstone Shard", "Tainted Worldstone Shard"],
            "Map Enhancers": ["Catalyst Shard", "Horadrim Scarab", "Standard of Heroes"],
            "Tokens": ["Token of Absolution", "Essence of Suffering", "Essence of Hatred", "Essence of Terror", "Essence of Destruction"],
            "Relics": ["Relic of the Ancients", "Sigil of Madawc", "Sigil of Talic", "Sigil of Korlic"],
            "Ubers": ["3x3 Uber Keys", "Key of Terror", "Key of Hate", "Key of Destruction"],
            "DC Clone": ["Vision of Terror", "Pure Demonic Essence", "Black Soulstone", "Prime Evil Soul"],
            "Rhatmas": ["Voidstone", "Splinter of the Void", "Trang-Oul's Jawbone", "Hellfire Ashes"]
        }

        for category, items in categories.items():
            with st.expander(category, expanded=False):
                for _, row in df[df["Name"].isin(items)].iterrows():
                    col1a, col1b = st.columns([3, 1])
                    with col1a:
                        st.markdown(f"<p class='item-name'>{row['Name']}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p class='item-price'>{row['Formatted Price']}</p>", unsafe_allow_html=True)
                    with col1b:
                        user_inputs[row['Name']] = st.number_input("", min_value=0, step=1, key=row['Name'])

    # 📊 Right Column - Summary
    with col2:
        st.subheader("📊 Summary")

        if st.button("🧾 Calculate Value"):
            st.write("Total value calculation here...")
