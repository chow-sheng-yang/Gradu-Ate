import pandas as pd
import plotly.express as px
import streamlit as st
import numpy as np
import altair as alt

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/

# How many MCs have I taken, and how much more do I need to complete (%) until graduation?
# What is my CGPA?
# How many MCs for each Core/GE/UE/Spec have I taken, and what is my completion rate (%) for each?
# What are the modules I took for each Core/GE/UE/Spec?
# Overall grade distribution
# CGPA over time

#######################
# Page configuration
st.set_page_config(
    page_title="NUS Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

#######################
# Helper Functions

def grade_point_mapper(grade):

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
        "S" : 0  
    }
    if grade in grade_point_mapping.keys():
        return grade_point_mapping[grade]
    return None
    
def cgpa_calculator(data):

    data = data[~(data['Grade'] == "S")]
    grade_point_vector = data['Grade'].apply(grade_point_mapper)
    units_vector = data['Units']
    cgpa = round(np.sum(grade_point_vector * units_vector) / sum(units_vector), 2)
    return cgpa

def get_track_requirements(track:str):
    if track == 'BBA-CORE':
        return 50
    elif track == 'GE':
        return 24
    elif track == 'BBA-HONS':
        return 20
    elif track == 'UE':
        return 46
    elif track.startswith('BBA-') and track != 'BBA-CORE':
        return 20
    elif track.startswith('MINOR-'):
        return 20
    elif track.startswith('MAJOR-'):
        return 40
    else:
        return None

def individual_track_progress(data):
    
    data = data.groupby('Module_Type').agg({'Units' : 'sum'}).reset_index()

    data['Track_Requirement'] = data['Module_Type'].apply(get_track_requirements)

    data['New_Module_Type'] = data['Module_Type'].apply(
        lambda x : (
            x if x in ['BBA-CORE', 'GE', 'BBA-HONS', 'UE', main_spec] else
            'UE' if x.startswith('MINOR-') else
            'UE' if x.startswith('MAJOR-') else
            'UE'
        )
    )

    data.loc[data['Module_Type']=='UE', 'Units'] = data[data['New_Module_Type']=='UE']['Units'].sum()

    data['Completion_Rate'] = ((data['Units'] / data['Track_Requirement'])*100).round(2)
   
    return data[['Module_Type', 'Completion_Rate']]

def individual_track_taken(data):
    return data[['Module_Code', 'Module_Type', 'Grade']]

def plot_metric_box(label, value:int):
    delta = +4
    st.markdown(
        f"""
        <div style="
            background-color: #FFFFFF;
            border: 1px solid #CCCCCC;
            border-left: 0.5rem solid #9AD8E1;
            border-radius: 6px;
            box-shadow: 0 0.15rem 1.75rem rgba(58, 59, 69, 0.1);
            padding: 1rem;
            margin-bottom: 1rem;
            width: 100%;
            text-align: center;
            font-family: 'Arial', sans-serif;
        ">
            <div style="font-size: 0.85rem; color: #444; font-weight: 600;">{label}</div>
            <div style="font-size: 1.75rem; font-weight: 400; color: #111;">{value}</div>
            <div style="font-size: 0.85rem; font-weight: 400; color: #000;">
                {'▲' if delta > 0 else '▼' if delta < 0 else ''} {abs(delta) if delta != 0 else ''}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

#######################
# Reading Data

@st.cache_data
def get_data_from_excel(file):

    if file is not None:
        return pd.read_excel(file, engine="openpyxl", sheet_name="data")
    return None

#######################
# Side Bar

with st.sidebar:

    st.title("NUS Dashboard")

    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
    df = get_data_from_excel(uploaded_file)
    if df is None:
        st.warning("Please upload your Excel file.")
        st.stop()

    module_type = st.multiselect(
        "Select the Specialisation:",
        options=df['Module_Type'].unique(),
        default=df['Module_Type'].unique()
    )

    df_selection = df.query(
        "Module_Type == @module_type"
    )

    if df_selection.empty:
        st.warning("No data available based on the current filter settings!")
        st.stop()

#######################
# Main Page

# -- Top Progress Bar:
num_MCs = int(df_selection["Units"].sum())
total_MCs_requirement = 160
completion_rate = round((num_MCs / total_MCs_requirement)*100, 1)

st.markdown(f"#### Completion Rate: {completion_rate}%")
st.progress(int(completion_rate))

# -- Side Metrics:
col1, col2 = st.columns((1, 2), gap='medium')

with col1:

    st.markdown('#### Overall Academic Metrics')

    plot_metric_box(label='Total MCs', value=num_MCs)
    plot_metric_box(label='Cumulative GPA', value=cgpa_calculator(df_selection))

    grade_counts = df_selection['Grade'].value_counts().reset_index()
    grade_counts.columns = ['Grade', 'Count']
    fig = px.pie(
        grade_counts, 
        names='Grade', 
        values='Count', 
        hole=0.4,
        title="Grade Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("""---""")

# -- Middle Panel:
with col2:

    st.markdown('#### Individual Track Analysis')

    table_col1, table_col2 = st.columns(2)

    with table_col1:
        main_spec = st.selectbox('Select your Main Specialisation', options=df_selection['Module_Type'].unique())
        individual_track_progress_df = individual_track_progress(df_selection)

        st.dataframe(individual_track_progress_df,
                    column_order=('Module_Type', 'Completion_Rate'),
                    hide_index=True,
                    width=None,
                    column_config={
                        "Module_Type": st.column_config.TextColumn("Module Type"),
                        "Units": st.column_config.NumberColumn("Units", format="%d"),
                        "Completion_Rate": st.column_config.ProgressColumn(
                            "Completion Rate",
                            format="%f",
                            min_value=0,
                            max_value=100
                        )}
                    )
        st.markdown(
        """
        <div style="
            background-color: #e8f4fd;
            border-left: 6px solid #2196F3;
            padding: 0.5rem;
            margin-top: 0.15rem;
            margin-bottom: 0.15rem;
            border-radius: 0.5rem;
            font-size: 0.95rem;
            color: #1a1a1a;
        ">
            <strong>📘 Note:</strong> Tracks that are not CORE, GE, HONS or Main Specialisation will count to UEs!
        </div>
        """,
        unsafe_allow_html=True
        )

    with table_col2:
        st.dataframe(individual_track_taken(df_selection))

#######################
# Hide Streamlit Style

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)