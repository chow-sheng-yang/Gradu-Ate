import pandas as pd
import plotly.express as px
import streamlit as st
import numpy as np
import altair as alt
import json

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/

#######################
# Page configuration

st.set_page_config(
    page_title="NUS Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

with open('track_requirements.json') as f:
    track_requirements = json.load(f)

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

def get_track_MC_requirements(track:str):
    if track.startswith('MINOR-'):
        return 20
    elif track.startswith('MAJOR-'):
        return 40
    else:
        return track_requirements[track]['MCs_required']

#######################
# User Class

class User:

    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.filtered_data = raw_data
        self.main_track = None
        self.individual_track_progress = None
    
    def apply_filter(self, selected_tracks):
        if selected_tracks:
            self.filtered_data = self.raw_data[self.raw_data['Module_Type'].isin(selected_tracks)]
        else:
            self.filtered_data = None
    
    def set_main_track(self, main_track):
        self.main_track = main_track

    def get_filtered_data(self):
        return self.filtered_data
    
    def get_total_MCs(self): # returns integer
        return int(self.filtered_data['Units'].sum()) 
    
    def get_completion_rate(self):
        total_MCs_requirement = 160
        return round((self.get_total_MCs() / total_MCs_requirement)*100, 1)
    
    def get_cgpa(self): # returns integer
        data = self.filtered_data[~(self.filtered_data['Grade'] == "S")]
        grade_point_vector = data['Grade'].apply(grade_point_mapper)
        units_vector = data['Units']
        cgpa = round(np.sum(grade_point_vector * units_vector) / sum(units_vector), 2)
        return cgpa 
    
    def get_individual_track_progress(self): # returns dataframe

        data = self.filtered_data.groupby('Module_Type').agg({'Units' : 'sum'}).reset_index()

        data['Track_Requirement'] = data['Module_Type'].apply(get_track_MC_requirements)

        data['New_Module_Type'] = data['Module_Type'].apply(
            lambda x : (
                x if x in ['BBA-CORE', 'GE', 'BBA-HONS', 'UE', self.main_track] else
                'UE' if x.startswith('MINOR-') else
                'UE' if x.startswith('MAJOR-') else
                'UE'
            )
        )

        data.loc[data['Module_Type']=='UE', 'Units'] = data[data['New_Module_Type']=='UE']['Units'].sum()

        data['Completion_Rate'] = ((data['Units'] / data['Track_Requirement'])*100).round(2)

        individual_track_progress = data[['Module_Type', 'Completion_Rate']]

        self.individual_track_progress = individual_track_progress
    
        return individual_track_progress
    
    def get_outstanding_modules(self):

        individual_track_progress = self.individual_track_progress

        incomplete_tracks = list(individual_track_progress[individual_track_progress['Completion_Rate'] < 100]['Module_Type'])

        incomplete_tracks_results = {}

        for track in incomplete_tracks:

            if track == 'BBA-HONS' or track == 'UE' or track.startswith("MINOR-") or track.startswith("MAJOR-"):
                continue

            required_courses = track_requirements[track]['Required_Courses']
            num_remaining_electives =  track_requirements[track]['Num_Remaining_Electives']
            completed_courses = list(self.filtered_data[self.filtered_data['Module_Type'] == track]['Module_Code'])

            if track == 'BBA-CORE':
                to_be_completed = list(set(required_courses) - set(completed_courses))

            if track == 'GE':
                to_be_completed = [prefix for prefix in required_courses if not any(item.startswith(prefix) for item in completed_courses)]

            if track.startswith('BBA-') and track != 'BBA-CORE':
                electives_taken = list(set(completed_courses) - set(required_courses))
                to_be_completed = list(set(required_courses) - set(required_courses))
                if len(electives_taken) < num_remaining_electives:
                    warning = f"You still have {num_remaining_electives - len(electives_taken)} number of electives for {track}!"

            # if track == 'UE':
            #     electives_taken = list(self.filtered_data[~self.filtered_data['Module_Type'].isin(['BBA-CORE', 'BBA-HONS', 'GE', self.main_track])]['Module_Code'])
            #     for i in electives_taken:
            #         st.markdown(f"-{i}")
            #     warning = f"You still have {num_remaining_electives - len(electives_taken)} number of electives for {track}!"

            incomplete_tracks_results[track] = to_be_completed + [warning]
        
        return incomplete_tracks_results.items()
    
        # identify which track is not at 100% completion rate
        # for track i, 
        #       collect all completed modules in a list
        #       obtain full list of requirements for track i
        #       if it is CORE/GE and all must be completed, simply compare which module exists in full list but not in completed list
        #       if it is SPEC, compare which compulsory modules need to be done and based on completion rate, how many more elective needed
        #       if it is HONS, 

#######################
# Functions for Main Panel Widgets

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

    user = User(df)

    selected_tracks = st.multiselect(
        "Select the Specialisation:",
        options=df['Module_Type'].unique(),
        default=df['Module_Type'].unique()
    )

    user.apply_filter(selected_tracks)

    if user.get_filtered_data() is None or user.get_filtered_data().empty:
        st.warning("No data available based on the current filter settings!")
        st.stop()

#######################
# Main Page

# -- Top Progress Bar:

completion_rate = user.get_completion_rate()
st.markdown(f"#### Completion Rate: {completion_rate}%")
st.progress(int(completion_rate))

# -- Side Metrics:
col1, col2 = st.columns((1, 2), gap='medium')

with col1:

    st.markdown('#### Overall Academic Metrics')

    plot_metric_box(label='Total MCs', value=user.get_total_MCs())

    plot_metric_box(label='Cumulative GPA', value=user.get_cgpa())

    grade_counts = user.get_filtered_data()['Grade'].value_counts().reset_index()
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

        data = user.get_filtered_data()

        main_track = st.selectbox('Select your Main Specialisation', options=data['Module_Type'].unique())

        user.set_main_track(main_track)

        st.dataframe(user.get_individual_track_progress(),
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
        for track, messages in user.get_outstanding_modules():
            st.markdown(f"**{track}:**")
            for msg in messages:
                st.markdown(f"- {msg}")

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