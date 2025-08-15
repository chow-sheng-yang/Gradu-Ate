import json
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd
import pickle
import streamlit as st
import base64
from pathlib import Path

'''
    1) This script contains helper functions needed across all other app scripts;
    2) This script is imported as a module.
'''

#######################
# Read App-related Data

# -- Read BBA Electives Course Descriptions:
with open('./data/bba_electives_description.pkl', 'rb') as f:
        course_descriptions = pickle.load(f)

# -- Read BBA Electives Information:
bba_electives_info = pd.read_excel('./data/bba_electives_info.xlsx')

# -- Read BBA Requirements:
with open('./data/bba_requirements.json') as f:
    bba_requirements = json.load(f)

# -- Read Demand Vacancy Compiled Data:
demand_vacancy_data = pd.read_csv('./data/demand_allocation.csv')

# -- Read GE Modules:
ge_mods = pd.read_excel("./data/nus_ge_requirements.xlsx")

# -- Read Recommender Module Ranking:
with open('./data/bba_electives_ranking.pkl', 'rb') as f:
        bba_electives_ranking = pickle.load(f)

#-- Read Recommender Module Demand-Vacancy:
with open('./data/bba_electives_demand_vacancy_data.pkl', 'rb') as f:
        bba_electives_demand_vacancy_data = pickle.load(f)
    
#######################
# Helper Functions to Load App-related Data

def load_bba_electives_description():
    return course_descriptions

def load_bba_electives_info():
    return bba_electives_info

def load_bba_requirements():
    return bba_requirements

def load_bba_electives_ranking():
    return bba_electives_ranking

def load_bba_electives_demand_vacancy_data():
    return bba_electives_demand_vacancy_data

def load_demand_vacancy_data():
    return demand_vacancy_data

def load_ge_requirements():
    return ge_mods

#######################
# Helper Functions

# -- Returns dictionary of {letter grade : numerical grade}:

def get_grade_mapping():
    grade_point_mapping = {
            "A+" : 5,
            "A" : 5,
            "A-" : 4.5,
            "B+" : 4,
            "B" : 3.5,
            "B-" : 3,
            "C+" : 2.5,
            "C" : 2,
            "D+" : 1.5,
            "D" : 1,
            "F" : 0,
            "S" : 0,
            "IP" : 0,
            "NG" : 0
        }
    return grade_point_mapping

# -- Returns numerical grade of a letter grade:

def grade_point_mapper(grade):
    grade_mapping = get_grade_mapping()
    if grade in grade_mapping.keys():
        return grade_mapping[grade]
    else:
        st.warning(f"Unrecognized grade: '{grade}' — unable to map to GPA.")
        return None  # or a default value like 0.0 or np.nan

# -- Returns list of BBA Electives across all Majors:

def return_all_bba_electives():
    res = []
    for track, data in bba_requirements.items():
        if track not in ['BBA-BE', 'BBA-BF', 'BBA-FSP']:
            if track == 'BBA-ACC':
                required_courses_list = data.get('Required_Courses')
                res.extend(required_courses_list)
            else:
                required_courses_list = data.get('Required_Courses')
                L3000_electives = data.get('3000_Electives').get('Courses')
                L4000_electives = data.get('4000_Electives').get('Courses')
                res.extend(required_courses_list)
                res.extend(L3000_electives)
                res.extend(L4000_electives)
    return list(res)
    
# -- Returns dictionary of {Module : Module_Type}

def return_flatten_bba_electives():
    res = {}
    for track, data in bba_requirements.items():
        for mod in data.get('Required_Courses'):
            res[mod] = track
        
        if '3000_Electives' in data:
            for mod in data.get('3000_Electives').get('Courses'):
                res[mod] = track
        
        if '4000_Electives' in data:
            for mod in data.get('4000_Electives').get('Courses'):
                res[mod] = track
    return res

# -- Returns Degree Classification based on CGPA:

def degree_classifier(cgpa):
    if cgpa >= 4.5:
        return "Honours | Highest Distinction"
    elif cgpa >= 4:
        return "Honours | Distinction"
    elif cgpa >= 3.5:
        return "Honours | Merit"
    elif cgpa >= 3:
        return "Honours"
    else:
        return "Pass"
    
# -- Constructs a proper Pandas Dataframe of User Progression Dictionary:

def normalize_completion_status(completion_status):
        rows = []

        for track, result in completion_status.items():
            # Check if result is a list or tuple with 3 items
            if isinstance(result, (list, tuple)) and len(result) == 3:
                completion_rate, status, cgpa = result
            else:
                # Fallback for bad or missing data
                completion_rate = None
                status = None
                cgpa = None

            rows.append({
                "Module_Type": track,
                "Completion_Rate": completion_rate,
                "Completion_Status": status,
                "CGPA": cgpa
            })

        res = pd.DataFrame(rows)

        res['Completion_Rate'].fillna(0, inplace=True)
        res['Completion_Status'] = res['Completion_Status'].apply(lambda x: x if isinstance(x, list) else [])
        res['CGPA'].fillna(0, inplace=True)
        return pd.DataFrame(res)

# -- Converts Hex to RGBA:

def hex_to_rgba(hex_color, alpha=0.3):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f'rgba({r}, {g}, {b}, {alpha})'

# -- Converts RGBA to Hex:

def rgba_to_hex(rgba):
    return '#{:02x}{:02x}{:02x}{:02x}'.format(
        int(rgba[0] * 255),
        int(rgba[1] * 255),
        int(rgba[2] * 255),
        int(rgba[3] * 255)
    )
# -- To render image icons:

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        b64_bytes = base64.b64encode(img_file.read())
        return b64_bytes.decode()
    
# -- Formats list of strings into single string with space:

def format_completion_list(series):
    return series.apply(lambda items: '<br>'.join(map(str, items)) if isinstance(items, list) else str(items))

# -- Returns decimals up, inclusive 0.5:

def round_half_up(value, decimals=2):
    value = Decimal(str(value))
    rounding_target = Decimal('1.' + '0' * decimals)
    return float(value.quantize(rounding_target, rounding=ROUND_HALF_UP))
# - Converts excel data into bytes (for sample download):

def load_excel_file_bytes(file_path):
    return Path(file_path).read_bytes()

# -- Converts px to rem:

def px_to_rem(px):
    return px / 16

# -- Converts rem to px:

def rem_to_px(rem):
    return rem * 16




#######################
# Helper Functions to Load User Excel File:

# -- Column Checking:

def validate_column(df, col, expected_type):

    # 1. Check if column exists
    if col not in df.columns:
        st.error(f"Column '{col}' is missing.")
        return False

    # 2. Check for null or empty values (NaN, empty strings)
    col_data = df[col]
    if col_data.isnull().any() or (col_data.astype(str).str.strip() == '').any():
        st.error(f"Column '{col}' contains null or empty values.")
        return False

    # 3. Check if values match the expected data type
    try:
        if expected_type == int:
            converted = pd.to_numeric(df[col], errors='raise')
        elif expected_type == float:
            converted = pd.to_numeric(df[col], errors='raise')
        elif expected_type == str:
            if not df[col].dropna().apply(lambda x: isinstance(x, str)).all():
                st.error(f"Column '{col}' must contain only string values.")
                return False
        else:
            st.error(f"Unsupported data type check for column '{col}'.")
            return False
    
    except Exception as e:
        st.error(f"Column '{col}' must contain only {expected_type.__name__} values. \
                 Please check again for typo/misspelled/invalid data in this column.")
        return False
    
    # 4. Special Check for Module_Type
    if col == 'Module_Type':
        allowed_MODULE_TYPES = {
            'BBA-BE', 'BBA-BF', 'BBA-FSP', 'GE', 'UE',
            'BBA-BZA', 'BBA-MKT', 'BBA-FIN', 'BBA-BSN',
            'BBA-BSE', 'BBA-DOS', 'BBA-RE', 'BBA-MNO', 'BBA-ACC'
        }

        def is_valid_MODULE_TYPE(value):
            if pd.isnull(value):
                return False
            value = str(value).strip().upper()
            return (
                value in allowed_MODULE_TYPES or
                value.startswith("MAJOR-") or
                value.startswith("MINOR-")
            )
        
        invalid_values = df[~df[col].apply(is_valid_MODULE_TYPE)][col].unique()
        if len(invalid_values) > 0:
            st.error(f"Column '{col}' contains invalid module types: {', '.join(map(str, invalid_values))}")
            return False
    
    # 5. Special Check for Grade
    if col == "Grade":

        allowed_GRADES = set(get_grade_mapping().keys())

        def is_valid_GRADE(value):
            if pd.isnull(value):
                return False
            return str(value).strip().upper() in allowed_GRADES
        
        invalid_grades = df[~df[col].apply(is_valid_GRADE)][col].unique()
        if len(invalid_grades) > 0:
            st.error(f"Column '{col}' contains invalid grade types: {', '.join(map(str, invalid_grades))}")
            return False
      
    # All checks passed
    return True

# -- Main Checks across entire dataset:

def load_uploaded_data(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file, sheet_name='data')
        EXPECTED_COLUMNS = ['Module_Code', 'Module_Title', 'Year', 'Semester', 'Units', 'Module_Type', 'Grade']

        # 1. Catch error if sheet is empty / no data
        if df.empty:
            st.error("Could not find any data in your excel file.")
            return None

        # 2. Check if expected columns are a subset of the uploaded columns
        if not set(EXPECTED_COLUMNS).issubset(set(df.columns)):
            st.error(f"The file is missing one or more required columns. \
                     Please ensure the columns are exactly: {EXPECTED_COLUMNS}")
            return None
        
        # 3. Only relevant columns
        df = df[EXPECTED_COLUMNS]

        # 4. Standardise upper case for string columns
        df['Module_Code'] = df['Module_Code'].str.upper()
        df['Module_Title'] = df['Module_Title'].str.upper()
        df['Module_Type'] = df['Module_Type'].str.upper()
        df['Grade'] = df['Grade'].str.upper()

        # 5. Validate each column
        expected_types = {
            'Module_Code': str,
            'Module_Title': str,
            'Year': int,
            'Semester': int,
            'Units': int,
            'Module_Type': str,
            'Grade': str
        }

        for col, expected_type in expected_types.items():
            check = validate_column(df=df, col=col, expected_type=expected_type)
            if not check:
                return None
        
        # 6. Check for exact duplicate rows (not double-counted or IP)
        duplicate_rows = df[df.duplicated()]
        if not duplicate_rows.empty:
            st.error(f"Your dataset contains duplicate row(s) for {duplicate_rows['Module_Code'].unique()}. Please remove them.")
            return None
                
        return df
    
    # Catch error if sheet name not properly formatted as 'data'
    except ValueError:
        st.error("Could not find the tab sheet 'data' in your excel file.")
        return None
    
    # Catch any other error
    except Exception as e:
        st.error("Error reading Excel file. Make sure it's properly formatted.")
        return None
    

