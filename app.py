import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import numpy as np
import altair as alt
import json
from helper_functions import grade_point_mapper, get_track_requirements
from grade_optimiser import GradeOptimizer
from collections import Counter
from user import User

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

#######################
# Functions for Main Panel Charts/Widgets

def render_note():
        st.markdown(
                """
                <div style="
                    background-color: #fff8e1;
                    border-left: 6px solid #fbc02d;
                    padding: 0.5rem;
                    margin-top: 0.15rem;
                    margin-bottom: 0.15rem;
                    border-radius: 0.5rem;
                    font-size: 0.95rem;
                    color: #1a1a1a;
                ">
                    <strong style="color:#f57f17;">⚠️ Note:</strong> Tracks that are not CORE, GE, HONS or Main Specialisation will count to UEs!
                </div>
                """,
                unsafe_allow_html=True
            )
        
def render_metric_box(label, value:int):
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

def render_completion_table(df):
    for _, row in df.iterrows():
        module = row['Module_Type']
        rate = row['Completion_Rate']

        st.markdown(f"""
        <div style="
            margin-bottom: 1rem;
            padding: 0.75rem 1rem;
            background: #fff;
            border-radius: 0.5rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        ">
            <strong style="color: #2a2a2a;">{module}</strong>
            <div style="
                margin-top: 0.4rem;
                height: 16px;
                background: #e6f2f8;
                border-radius: 999px;
                overflow: hidden;
            ">
                <div style="
                    width: {rate}%;
                    height: 100%;
                    background: linear-gradient(90deg, #2ec4b6, #00b4d8);
                    transition: width 1s ease-in-out;
                "></div>
            </div>
            <p style="margin: 0.25rem 0 0; font-size: 0.85rem; color: #555;">
                {rate:.2f}%
            </p>
        </div>
        """, unsafe_allow_html=True)

def render_grade_chart(actual_counts: dict, target_counts: dict):
    df_actual = pd.DataFrame(list(actual_counts.items()), columns=['Grade', 'Count'])
    df_target = pd.DataFrame(list(target_counts.items()), columns=['Grade', 'Count'])
    df_actual['Type'] = 'Actual'
    df_target['Type'] = 'Target'

    # Convert grades to string to avoid sorting errors
    df_actual['Grade'] = df_actual['Grade'].astype(str)
    df_target['Grade'] = df_target['Grade'].astype(str)

    # Combine all grades to get consistent sorting order
    all_grades = sorted(set(df_actual['Grade']) | set(df_target['Grade']))
    df_actual['Grade'] = pd.Categorical(df_actual['Grade'], categories=all_grades, ordered=True)
    df_target['Grade'] = pd.Categorical(df_target['Grade'], categories=all_grades, ordered=True)

    # Combine both dataframes for layered chart
    df_combined = pd.concat([df_target, df_actual])

    # Create chart with color encoding by Type for legend
    chart = alt.Chart(df_combined).mark_bar().encode(
        y=alt.Y('Grade:N', sort=all_grades, title='Grade'),
        x=alt.X('Count:Q', title='Count', scale=alt.Scale(domain=[0, df_combined['Count'].max() + 1])),
        color=alt.Color('Type:N',
                        scale=alt.Scale(domain=['Target', 'Actual'],
                                        range=['#d3e9f6', '#29b5e8']),
                        legend=alt.Legend(title="Legend")),
        tooltip=['Grade', 'Count', 'Type']
    ).properties(
        width=300,
        height=300
    ).configure_view(
        stroke=None
    )

    st.altair_chart(chart, use_container_width=True)

def render_completion_donut(completion_rate, label, color_theme):

    color_map = {
        'blue': ['#29b5e8', '#cceefa'],
        'green': ['#27AE60', '#c2f0d1'],
        'orange': ['#F39C12', '#fce6c5'],
        'red': ['#E74C3C', '#f5cccc']
    }

    chart_color = color_map.get(color_theme, color_map['blue'])

    # Data
    source = pd.DataFrame({
        "Label": ['', label],
        "Value": [100 - completion_rate, completion_rate]
    })
    source_bg = pd.DataFrame({
        "Label": ['', label],
        "Value": [100, 0]
    })

    # Chart
    plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=80, cornerRadius=15).encode(
        theta="Value:Q",
        color=alt.Color("Label:N",
                        scale=alt.Scale(domain=[label, ''], range=chart_color),
                        legend=None)
    ).properties(width=200, height=200)

    plot = alt.Chart(source).mark_arc(innerRadius=80, cornerRadius=15).encode(
        theta="Value:Q",
        color=alt.Color("Label:N",
                        scale=alt.Scale(domain=[label, ''], range=chart_color),
                        legend=None)
    ).properties(width=200, height=200)

    text = alt.Chart(pd.DataFrame({'text': [f"{completion_rate:.1f}%"]})).mark_text(
        font="Lato", fontSize=26, fontWeight="bold", color=chart_color[0]
    ).encode(text='text:N')

    donut_chart = plot_bg + plot + text

    # Card wrapper
    with st.container():
        st.markdown(f"""
            <div style="
                margin-bottom: 1rem;
                padding: 1rem;
                background: #fff;
                border-radius: 0.5rem;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                text-align: center;
            ">
                <strong style="color: #2a2a2a; font-size: 1.05rem;">{label}</strong>
            """, unsafe_allow_html=True)

        st.altair_chart(donut_chart, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

        
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

# -- Side Bar Title:

    st.markdown("## 🎓 NUS Dashboard")

# -- User Information:

    name = st.text_input("👤 Enter your name")
    year = st.selectbox("📅 Year of Study", options=["1", "2", "3", "4", "5+"], index=0)
    faculty = st.selectbox("🏛️ Faculty", options=["School of Business", "Engineering", "FASS", "Computing", "Science", "Others"], index=0)

# -- User Upload File Section:

    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
    df = get_data_from_excel(uploaded_file)
    if df is None:
        st.warning("Please upload your Excel file.")
        st.stop()

    user = User(user_name=name, user_year=year, user_faculty=faculty, raw_data=df)

# -- User Select Specialisation Section:

    selected_tracks = st.multiselect(
        "Select the tracks you want to view:",
        options=df['Module_Type'].unique(),
        default=df['Module_Type'].unique()
    )

    specialisation_options = [track for track in selected_tracks if \
                              (track.startswith('BBA-')) and \
                              (track != "BBA-CORE") and \
                              (track != "BBA-HONS")]
    main_track = st.selectbox('Select your main track/specialisation:', 
                            options=specialisation_options)

    user.set_main_track(main_track)

    user.apply_filter(selected_tracks)

    if user.get_filtered_data() is None or user.get_filtered_data().empty:
        st.warning("No data available based on the current filter settings!")
        st.stop()

# -- Note:

    render_note()

#######################
# Main Page

# -- Top User Information Display:

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown(f"""
        # 👋 Hi {user.user_name if user.user_name else "Student"}!
        ### 🎯 Here's your Graduation Report:
    """)

# -- Top Progress Donut:

completion_rate = user.snapshot.completion_rate
completion_rate = min(completion_rate, 100)

with col2:
    st.markdown('#### Overall Academic Metrics')

    render_metric_box(label='Total MCs', value=user.snapshot.total_units)

    render_metric_box(label='Cumulative GPA', value=user.snapshot.cgpa)

with col3:
    render_completion_donut(
        completion_rate=completion_rate, 
        label=f"⏳ You are left with {user.user_year_left} year(s) to go!",
        color_theme='blue'
    )

st.markdown("""---""")

# -- Side Panel:
col1, col2 = st.columns((1, 2), gap='medium')

with col1:
    st.markdown('#### Letter Grade Distribution')

    grade_optimiser = GradeOptimizer(df=user.filtered_data, threshold=user.snapshot.cgpa)
    grade_optimiser_results = grade_optimiser.run()
    # Debug outputs
    st.write("✅ Total Units:", grade_optimiser.total_units)
    st.write("📚 Fixed GPA Sum:", grade_optimiser.fixed_gpa_sum)
    st.write("📈 SIM GPA Value:", grade_optimiser.sim_gpa_value)
    st.write("📉 Penalty Value:", grade_optimiser.penalty_value)
    st.write("🎯 CGPA:", grade_optimiser.cgpa_value)

    if grade_optimiser_results is not None:
        grade_optimiser_grades_list = grade_optimiser_results['selected_letters']
        st.write(grade_optimiser_grades_list)
    else:
        st.warning("No feasible grade combination found to meet the CGPA threshold.")

    actual_counts = user.snapshot.grade_distribution
    target_counts = dict(Counter(grade_optimiser_grades_list) + Counter(actual_counts))

    render_grade_chart(actual_counts=actual_counts, target_counts=target_counts)

# -- Middle Panel:
with col2:

    st.markdown('#### Individual Track Analysis')

    table_col1, table_col2 = st.columns(2)

    with table_col1:

        completion_status, remaining_status = user.snapshot.track_completion_df, user.snapshot.track_remaining

        render_completion_table(completion_status)

    with table_col2:
        for track, status in remaining_status:
            if status:
                with st.expander(f"📘 {track} - Click to view outstanding requirements"):
                    st.markdown(
                        f"""
                        <div style="
                            background-color: #f0f8ff;
                            border-left: 6px solid #007acc;
                            padding: 0.75rem 1rem;
                            margin-bottom: 0.5rem;
                            border-radius: 0.5rem;
                            font-size: 0.95rem;
                            color: #1a1a1a;
                        ">
                            <strong style="color:#007acc;">🔍 Outstanding Requirements:</strong><br>
                            You have <em>{', '.join(str(s) for s in status)}</em> to complete!
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

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