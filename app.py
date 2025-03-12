import pandas as pd
import ipywidgets as widgets
import re
from IPython.display import display

# 📥 Load Excel file
file_path = '/content/data.xlsx'  # Ensure the file is uploaded

# Load only the 'Trade Values' sheet with the correct header
df = pd.read_excel(file_path, sheet_name='Trade Values', header=1, dtype=str)

# 🌟 **Remove empty rows that may affect indexing**
df.dropna(how='all', inplace=True)  # Removes rows where all values are NaN

# 🌟 **Combine 'Number' and 'Rune' columns into a single 'Name' column**
df['Name'] = df['Number'].astype(str).str.strip() + ' ' + df['Rune'].astype(str).str.strip()

# 🌟 **Rename price columns**
df.rename(columns={
    'HR value': 'HR',
    'GV (Gul value)': 'GUL',
    'WSS value': 'WSS'
}, inplace=True)

# 🌟 **Remove empty rows and duplicates**
df = df[['Name', 'HR', 'GUL', 'WSS']]
df = df[df['Name'].str.strip() != '']  # Remove empty product names
df.drop_duplicates(subset=['Name'], keep='first', inplace=True)  # Remove duplicates


# 🌟 **Clean product names**
def clean_name(name):
    name = re.sub(r'\(.*?\)', '', name)  # Remove parentheses and their contents
    name = name.replace(' nan', '').strip()  # Remove 'nan' labels
    return name


df['Name'] = df['Name'].apply(clean_name)

# 🌟 **Remove unwanted rows**
df = df[~df['Name'].isin(['nan', 'PD2 Currency Data', 'Number Rune'])]


# 🔹 **Function to parse value ranges**
def parse_min_max(value):
    if isinstance(value, str):
        value = value.replace(',', '.').strip()  # Replace commas with dots, trim spaces
        if '-' in value:
            try:
                numbers = [float(x.strip()) for x in value.split('-')]
                return numbers[0], numbers[1]  # Min and Max
            except ValueError:
                return 0, 0
    try:
        num = float(value)
        return num, num  # If a single value, min = max
    except (ValueError, TypeError):
        return 0, 0


# 🔹 **Process price values**
df[['HR Min', 'HR Max']] = df['HR'].astype(str).apply(parse_min_max).apply(pd.Series)
df[['GUL Min', 'GUL Max']] = df['GUL'].astype(str).apply(parse_min_max).apply(pd.Series)
df[['WSS Min', 'WSS Max']] = df['WSS'].astype(str).apply(parse_min_max).apply(pd.Series)

# 🔹 **Remove old price columns**
df.drop(columns=['HR', 'GUL', 'WSS'], inplace=True)

# 🔹 **Replace NaN with 0 and convert to float**
df.fillna(0, inplace=True)
df[['HR Min', 'HR Max', 'GUL Min', 'GUL Max', 'WSS Min', 'WSS Max']] = df[
    ['HR Min', 'HR Max', 'GUL Min', 'GUL Max', 'WSS Min', 'WSS Max']].astype(float)

# 🔹 **Create input fields for quantities**
quantity_inputs = {}
for index, row in df.iterrows():
    quantity_inputs[row['Name']] = widgets.HBox([
        widgets.Label(value=str(row['Name']), layout=widgets.Layout(width='300px')),
        widgets.IntText(value=0, min=0, layout=widgets.Layout(width='100px'))
    ])


# 🔹 **Function to calculate values based on user input**
def calculate_values(change=None):
    total_hr_min, total_hr_max = 0, 0
    total_gul_min, total_gul_max = 0, 0
    total_wss_min, total_wss_max = 0, 0

    for index, row in df.iterrows():
        quantity = quantity_inputs[row['Name']].children[1].value
        total_hr_min += quantity * row['HR Min']
        total_hr_max += quantity * row['HR Max']
        total_gul_min += quantity * row['GUL Min']
        total_gul_max += quantity * row['GUL Max']
        total_wss_min += quantity * row['WSS Min']
        total_wss_max += quantity * row['WSS Max']

    # 🔹 **Display results**
    print("\n📊 Summary:")
    print(f"✔️ Total value (HR): {total_hr_min:.2f} - {total_hr_max:.2f}")
    print(f"✔️ Total value (Gul): {total_gul_min:.2f} - {total_gul_max:.2f}")
    print(f"✔️ Total value (WSS): {total_wss_min:.2f} - {total_wss_max:.2f}")


# 🔹 **Display user interface**
print("🛍️ Select product quantities:")
for input_field in quantity_inputs.values():
    display(input_field)

# 🔹 **Button to calculate values**
calculate_button = widgets.Button(description="Calculate Value")
calculate_button.on_click(calculate_values)
display(calculate_button)
