import streamlit as st
import pandas as pd
import re

# 📌 Page configuration - enforce 80% width
st.set_page_config(page_title="PD2 Pricing App", layout="wide")
st.markdown("""
    <style>
        .appview-container .main .block-container {
            max-width: 55% !important;
            margin: 0 auto !important;
            padding-top: 0 !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("💰 PD2 Pricing App")
st.markdown("Upload your Excel file and calculate item prices.")
st.markdown('<div class="app-container">', unsafe_allow_html=True)

# 🎨 Custom CSS for better UI
st.markdown("""
    <style>
        .stButton>button { width: 100%; padding: 10px; font-size: 18px; }
        .summary-box { 
            border: 2px solid #4CAF50; padding: 15px; border-radius: 10px; 
            background-color: #f9f9f9; text-align: center;
        }
        .summary-title { font-size: 22px; font-weight: bold; color: #4CAF50; }
        .summary-value { font-size: 18px; margin-bottom: 10px; }
        .item-container {
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #f9f9f9;
            margin-bottom: 3px;
            width: 100%;
        }
        }
        .item-header { display: flex; justify-content: space-between; width: 100%; align-items: center; }
        .item-name { 
            font-size: 18px !important; 
            font-weight: bold !important; 
            margin-bottom: 2px !important;
        }
        .item-price { 
            font-size: 14px !important; 
            font-style: italic !important; 
            color: gray !important; 
            margin-top: 0px !important;
        }
        } 
        .item-input {
            width: 60px !important; 
            height: 30px !important; 
            border-radius: 5px !important;
            border: 1px solid #ccc !important;
            text-align: center !important;
            font-size: 14px !important;
            margin-left: 10px !important;
            padding: 2px !important;
        }
        .stNumberInput {
            width: 50px !important; 
            height: 30px !important; 
            border-radius: 5px !important;
            border: 1px solid #ccc !important;
            text-align: center !important;
            margin-left: auto !important;  
        }
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
        name = re.sub(r'\(.*?\)', '', name)
        name = name.replace(' nan', '').strip()
        name = re.sub(r'^(1[8-9]|2[0-9]|3[0-3])\s', '', name)
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

    # 📌 Define categories (FULL LIST AS REQUESTED)
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

    # 🎛️ UI with two columns
    col1, col2 = st.columns([2, 1])

    user_inputs = {}

    # 🎛️ Left Column - Grouped Items
    user_inputs = {}  # Przechowywanie wartości wpisanych przez użytkownika

    with col1:
        st.subheader("🛍️ Select item quantities:")
        for category, items in categories.items():
            with st.expander(category, expanded=False):  # Grupy domyślnie zwinięte
                for _, row in df[df["Name"].isin(items)].iterrows():
                    with st.container():
                        col_left, col_right = st.columns([4, 1])  # Nazwa + wartości (4) | Input (1)

                        with col_left:
                            st.markdown(f"""
                                <div class="item-container">
                                    <p class="item-name">{row['Name']}</p>
                                    <p class="item-price">
                                        HR: {row['HR Min']:.2f}-{row['HR Max']:.2f}, 
                                        Gul: {row['GUL Min']:.2f}-{row['GUL Max']:.2f}, 
                                        WSS: {row['WSS Min']:.2f}-{row['WSS Max']:.2f}
                                    </p>
                                </div>
                            """, unsafe_allow_html=True)

                        with col_left:  # 🔹 Input teraz jest w tej samej kolumnie, co nazwa i cena
                            user_inputs[row['Name']] = st.number_input(
                                "", min_value=0, step=1, key=row['Name']
                            )

    # 📊 Right Column - Summary
    with col2:
        st.subheader("📊 Summary")

        if st.button("🧾 Calculate Value"):
            total_hr_min = 0
            total_hr_max = 0
            total_gul_min = 0
            total_gul_max = 0
            total_wss_min = 0
            total_wss_max = 0

            for name, row in df.set_index('Name').iterrows():
                quantity = user_inputs.get(name, 0)
                if quantity > 0:
                    total_hr_min += quantity * row['HR Min']
                    total_hr_max += quantity * row['HR Max']
                    total_gul_min += quantity * row['GUL Min']
                    total_gul_max += quantity * row['GUL Max']
                    total_wss_min += quantity * row['WSS Min']
                    total_wss_max += quantity * row['WSS Max']

            # 🔥 Wyświetlenie poprawnej sumy wartości
            st.markdown(f"""
                <div class='summary-box'>
                    <p class='summary-title'>🧾 Total Value</p>
                    <p class='summary-value'><strong>HR:</strong> {total_hr_min:.2f} - {total_hr_max:.2f}</p>
                    <p class='summary-value'><strong>Gul:</strong> {total_gul_min:.2f} - {total_gul_max:.2f}</p>
                    <p class='summary-value'><strong>WSS:</strong> {total_wss_min:.2f} - {total_wss_max:.2f}</p>
                </div>
            """, unsafe_allow_html=True)