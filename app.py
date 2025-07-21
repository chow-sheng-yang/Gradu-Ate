import pandas as pd
import numpy as np

import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import to_hex
import altair as alt

import streamlit as st
from collections import Counter

from utils import *
from user import User
from statsmodels.nonparametric.smoothers_lowess import lowess


import torch
import torch.nn.functional as F
import pickle
from Embed_Modules import preprocess_text

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

# -- Background Gradient:

st.markdown("""
    <style>
    body {
        background-color: #0d1b2a;  /* solid dark blue */
    }

    [data-testid="stAppViewContainer"] > .main {
        background-color: #0d1b2a;
        color: white;
    }

    [data-testid="stSidebar"] {
        background-color: #0d1a2d;
    }

    .stButton > button, .stTextInput > div > div > input {
        background-color: #102030 !important;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# -- Colors:

dba_hex = [to_hex(c) for c in sns.color_palette('Blues', n_colors=4)]
scm_hex = [to_hex(c) for c in sns.color_palette('Oranges', n_colors=4)]

# -- Coloring Multi-Select Boxes:

st.markdown(f"""
    <style>
    .stMultiSelect [data-baseweb="tag"] {{
        background-color: {dba_hex[3]} !important;
        color: white !important;
    }}
    </style>
""", unsafe_allow_html=True)

# -- Change Side Bar Color:

st.markdown("""
    <style>
    [data-testid="stSidebar"] > div:first-child {
        height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #0d1a2d, #1e324a);
        color: #ffffff;
    }

    [data-testid="stSidebar"] .css-1v0mbdj,
    [data-testid="stSidebar"] .css-10trblm {
        color: #ffffff;
    }

    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label {
        color: #ffffff;
        font-weight: 600;
    }

    [data-testid="stSidebar"] .stSelectbox,
    [data-testid="stSidebar"] .stMultiSelect {
        background-color: #22384f;
        border: 1px solid #00E0FF;
        border-radius: 8px;
    }

    [data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
        background-color: #00E0FF;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

#######################
# Functions for Main Panel Charts/Widgets

def hex_to_rgba(hex, alpha=0.3):
    rgb = mcolors.hex2color(hex)  # (r, g, b) as floats 0-1
    return f'rgba({int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)}, {alpha})'

def render_note(message):
   st.markdown(
        f"""
        <div style="
            background-color: #0d1a2d;
            border-left: 6px solid #df740c;
            padding: 0.5rem;
            margin-top: 0.15rem;
            margin-bottom: 0.15rem;
            border-radius: 0.5rem;
            font-size: 1.15rem;
            color: #FFFFFF;
            font-family: 'Arial', sans-serif;
        ">
            <strong>⚠️ Note:</strong> {message}
        </div>
        """,
        unsafe_allow_html=True
    )
   
def render_CGPA_box(label, value:int):
    delta = round(user.snapshot.cgpa - user.snapshot.prev_cgpa, 2)

    # Determine delta sign and color
    if delta > 0:
        delta_symbol = '▲'
        delta_color = '#00FF88'  # green
        delta_msg = f"by {abs(delta)} from {user.snapshot.prev_cgpa}" 
    elif delta < 0:
        delta_symbol = '▼'
        delta_color = '#FF5555'  # red
        delta_msg = f"by {abs(delta)} from {user.snapshot.prev_cgpa}" 
    else:
        delta_symbol = ''
        delta_color = '#FFFFFF'  # neutral white if needed
        delta_msg = f"No change from {user.snapshot.prev_cgpa}" 
    
    delta_display = f"{delta_symbol} | {delta_msg}"

    st.markdown(
        f"""
        <div style="
            background: rgba(13,26,45,0.98);
            border-radius: 0rem;
            width: 400px;
            height: 260px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            font-family: 'Arial', sans-serif;
            margin-bottom: 1rem;
            border: 3px solid #df740c;
            box-shadow: 0 0 12px #df740c88;
        ">
            <div style="
                font-size: 1.2rem; 
                color: #df740c; 
                font-weight: 400;
                text-shadow: 0 0 6px #df740cbb;
            ">{label}</div>
            <div style="
                font-size: 4rem; 
                font-weight: 500; 
                color: #df740c; 
                margin: 0.5rem 0;
                text-shadow: 0 0 8px #df740ccc;
            ">{value}</div>
            <div style="
                font-size: 1.25rem; 
                font-weight: 400; 
                color: {delta_color};
                text-shadow: 0 0 6px {delta_color}88;
            ">{delta_display}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_metric_box(label, value:int):
    delta = +4
    st.markdown(
        f"""
        <div style="
            background: rgba(13,26,45,0.98);
            border-radius: 0rem;
            width: 400px;
            height: 260px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            font-family: 'Arial', sans-serif;
            margin-bottom: 1rem;
        ">
            <div style="font-size: 1.2rem; color: #dddddd; font-weight: 400;">{label}</div>
            <div style="font-size: 4rem; font-weight: 500; color: #FFFFFF; margin: 0.5rem 0;">{value}</div>
            <div style="font-size: 1.25rem; font-weight: 400; color: #00E0FF;">
                {'▲' if delta > 0 else '▼' if delta < 0 else ''} {abs(delta) if delta != 0 else ''}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_degree_completion(completion_rate, label):

    fig = go.Figure(data=[go.Pie(
        values=[completion_rate, 100 - completion_rate],
        labels=['Completed', 'Remaining'],
        hole=0.80,
        marker=dict(colors=['#7DFDFE', '#df740c']),
        textinfo='none',
        domain=dict(x=[0.1, 0.9], y=[0.1, 0.9])
    )])

    fig.update_layout(
        showlegend=False,
        height=260,
        width=200,
        margin=dict(t=0, b=0, l=0, r=0),
        annotations=[dict(
            text=f"<b>{completion_rate:.0f}%</b>",
            x=0.5, y=0.5,
            font_size=50,
            showarrow=False,
            font_color="white"
        )],
        paper_bgcolor="#0d1a2d",
        plot_bgcolor="#0d1a2d"
    )

    st.plotly_chart(fig)

def render_completion_table(df):

    st.dataframe(df,
                 column_order=("Module_Type", "Completion_Rate", "Completion_Status"),
                 hide_index=True,
                 width=None,
                 height=500,
                 column_config={
                    "Module_Type": st.column_config.TextColumn(
                        "Track",
                    ),
                    "Completion_Rate": st.column_config.ProgressColumn(
                        "Completion Rate",
                        format="%f",
                        min_value=0,
                        max_value=max(df['Completion_Rate']),
                     ),
                     "Completion_Status": st.column_config.TextColumn(
                        "What You Need To Complete",
                    )}
                 )
    
def render_bar_chart(df):

    df = df.sort_values(by='avg_GPA', ascending=True)

    fig = go.Figure()

    fig.add_trace(go.Bar(
    x=df['Module_Type'],
    y=df['avg_GPA'],
    marker=dict(
        color='#df740c',
        line=dict(color='#df740c', width=1.5)
    ),
    text=df['avg_GPA'].round(2),
    textposition='outside',
    hovertemplate='<b>%{y}</b><br>CGPA: %{x:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title=dict(
            text="GPA Distribution by Track",
            font=dict(size=25, color="#FFFFFF", family="Arial, sans-serif"),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(title='Track', tickfont=dict(size=14, color="#FFFFFF")),
        yaxis=dict(title='Average GPA', range=[min(df['avg_GPA'])-0.05, 5.0], tickfont=dict(size=14, color="#FFFFFF")),
        height=500,
        margin=dict(l=60, r=40, t=120, b=40),
        plot_bgcolor='#0d1a2d',
        paper_bgcolor='#0d1a2d',
        showlegend=False,
        bargap=0.5
    )

    st.plotly_chart(fig, use_container_width=True)
    
def render_waterfall_chart(df):

    cgpa_vector, measure_vector, year_vector = [], [], []

    for term in sorted(df['Term'].unique()):

        data = df[df['Term'] <= term]
        
        cgpa = compute_cgpa(data)
    
        cgpa_vector.append(cgpa)

        if term == min(df['Term']):
            measure_vector.append('absolute')
        else:
            measure_vector.append('relative')
        
        term = str(term)
        year_vector.append(f'Y{term[0]}S{term[1]}')

    cgpa_vector = round_half_up(pd.Series(cgpa_vector), 2)
    change_vector = cgpa_vector.diff()
    change_vector.iloc[0] = cgpa_vector.iloc[0]
    change_vector = change_vector

    plot_df = pd.DataFrame({
        'Term': year_vector,
        'CGPA': cgpa_vector,
        'CGPA_Delta' : change_vector,
        'Measure' : measure_vector
    })


    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=plot_df['Term'],
        y=plot_df['CGPA'],
        mode='lines+markers',
        line=dict(color='#df740c', width=3, shape='spline'),
        marker=dict(size=8, color='#df740c'),
        name='CGPA Trend'
    ))

    # Vertical gradient fill layers below line
    for i, alpha in enumerate([
        0.20, 0.17, 0.14, 0.115, 0.09, 0.07, 0.055, 0.045,
        0.035, 0.027, 0.02, 0.015, 0.011, 0.008, 0.005, 0.003,
        0.0015, 0.0008, 0.0003, 0.0
    ]):
        y_offset = plot_df['CGPA'] - (i + 1) * 0.04
        fig.add_trace(go.Scatter(
            x=plot_df['Term'],
            y=y_offset,
            mode='lines',
            line=dict(width=0),
            fill='tonexty',
            fillcolor=f'rgba(223,116,12,{alpha})',
            hoverinfo='skip',
            showlegend=False
        ))

    # Add delta annotations
    for i, (x, delta) in enumerate(zip(plot_df['Term'], plot_df['CGPA_Delta'])):
        fig.add_annotation(
            x=x,
            y=plot_df['CGPA'].iloc[i] + 0.03,  # position above point
            text=f"{delta:+.2f}",
            showarrow=False,
            font=dict(size=20, color="white", family='Courier New'),
            borderwidth=1,
            borderpad=4
        )

    fig.update_layout(
        title=dict(
            text="CGPA Change Over Semesters",
            font=dict(size=25, color="#FFFFFF", family="Arial, sans-serif"),
            x=0.5,
            xanchor='center'
        ),
        yaxis_title="CGPA",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor='rgba(13,26,45,0.98)',
        xaxis=dict(showgrid=False, tickfont=dict(size=20, color="#FFFFFF")),
        yaxis=dict(range=[min(cgpa_vector)-0.2, max(cgpa_vector)+0.2], showgrid=False, tickfont=dict(size=20, color="#FFFFFF")),
        height=500,
        margin=dict(l=40, r=40, t=120, b=40),
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)

def render_treemap(df):

    fig = go.Figure(go.Treemap(
        labels=df['Module_Code'],
        values=df['TFIDF_Sim'],
        parents=[""] * len(df),
        textinfo="label",
        textfont=dict(size=20, color='white'),
        marker=dict(
            colors=df['TFIDF_Sim'],
            colorscale=[[0, '#DF740C'], [1, '#EE0000']],
            line=dict(width=1, color="#FFA500"),
            showscale=True
        ),
        root=dict(color='rgba(20,36,59,0.98)')
    ))

    fig.update_layout(
        title=dict(
            text="Recommended Modules",
            font=dict(size=25, color="#FFFFFF", family="Arial, sans-serif"),
            x=0.5,
            xanchor='center'
        ),
        height=900,
        plot_bgcolor='rgba(13,26,45,0.98)',
        paper_bgcolor='rgba(13,26,45,0.98)',
        margin=dict(t=80, l=40, r=40, b=40)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def recommend_modules(user_input, k=10):

    if not isinstance(user_input, str):
        return None
    
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    with open('course_descriptions.pkl', 'rb') as f:
        course_descriptions = pickle.load(f)

    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(course_descriptions['Module_Description'])

    user_input = preprocess_text(user_input)
    user_vec = tfidf_vectorizer.transform([user_input])
    tfidf_sims = cosine_similarity(tfidf_matrix, user_vec).flatten()

    course_descriptions['TFIDF_Sim'] = tfidf_sims
    top_k_matches = course_descriptions.sort_values(by='TFIDF_Sim', ascending=False).head(10)

    return top_k_matches

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

# -- Reading Data & Preprocessing:

    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
    df = get_data_from_excel(uploaded_file)

    if df is None:
        st.warning("Please upload your Excel file.")
        st.stop()
    else:
        df['GPA'] = df['Grade'].map(grade_point_mapper)
        df['Term'] = (df['Year'].astype(str) + df['Semester'].astype(str)).astype(int)
        year_long_mods = df.groupby('Module_Code')['Semester'].nunique().loc[lambda x: x > 1].index
        df_year_long = df[df['Module_Code'].isin(year_long_mods)].groupby('Module_Code').agg({
            'Module_Title': 'first',
            'Year': 'max',
            'Semester': 'max',
            'Units': 'sum',
            'Module_Type': 'first',
            'Grade': 'first',
            'Remarks': 'first',
            'GPA': 'first',
            'Term': 'max'
        }).reset_index()

        df_not_year_long = df[~df['Module_Code'].isin(year_long_mods)]

        df = pd.concat([df_year_long, df_not_year_long], ignore_index=True)

# -- Side Bar Title:

    st.markdown("# 🎓 NUS Dashboard")

# -- User Configuration:

    if "user" not in st.session_state:
        st.session_state.user = User(raw_data=df)

    user = st.session_state.user

# -- Select Tracks:

    selected_tracks = st.multiselect(
        "Select the tracks you want to view:",
        options=df['Module_Type'].unique(),
        default=df['Module_Type'].unique()
    )

# -- Select Main Specialisation:

    specialisation_options = [track for track in selected_tracks if \
                              (track.startswith('BBA-')) and \
                              (track != "BBA-CORE") and \
                              (track != "BBA-HONS")]
    main_track = st.selectbox('Select your main track/specialisation:', 
                            options=specialisation_options)

# -- Input Text Message for Module Recommendation:
    
    modrec_input = st.text_area("Based on your Main Specialisation, describe areas of interest for Module Recommendation:",
                                 value='e.g I am interested in Marketing, Consumer Behaviour, Consumer Research',
                                 height=150)

# -- Filtering Process:

    user.set_main_track(main_track)
    user.apply_filter(selected_tracks)

    if user.get_filtered_data() is None or user.get_filtered_data().empty:
        st.warning("No data available based on the current filter settings!")
        st.stop()

# -- Note Card:

    note = "Tracks that are not CORE, GE, HONS or Main Specialisation will count to UEs!"
    render_note(note)

#######################
# Main Page

# -- Top Metrics:

completion_rate = user.snapshot.completion_rate
completion_rate = min(completion_rate, 100)

box1, box2, box3, box4, box5 = st.columns(5, gap='small')

with box1:
    render_metric_box(label='Total MCs', value=user.snapshot.total_units)
with box2:
    render_CGPA_box(label='Cumulative GPA', value=user.snapshot.cgpa)
with box3:
    render_metric_box(label='Remaining S/Us', value= (32 - (user.snapshot.SU_used * 4)))
with box4:
    render_metric_box(label='Year of Study', value= user.snapshot.current_year)
with box5:
    render_degree_completion(
        completion_rate=completion_rate, 
        label=f"⏳ You are left with {4 - user.snapshot.current_year} year(s) to go!",
)

st.markdown("""---""")

# -- Bottom Side Panel:
col1, col2 = st.columns((0.75, 0.25), gap='medium')

with col1:

    render_waterfall_chart(df=user.filtered_data)

    col3, col4 = st.columns((1, 1), gap='medium')
    
    with col3: 
        track_status = user.snapshot.track_status
        render_completion_table(track_status)

    with col4:
        track_gpas = user.filtered_data.groupby('Module_Type').agg(avg_GPA=('GPA', np.mean)).reset_index()
        render_bar_chart(track_gpas)

# -- Bottom Middle Panel:

with col2:

    if modrec_input:
        res = recommend_modules(user_input=modrec_input)
        render_treemap(res)
        note = (
            "These module recommendations are generated by the algorithm to the best of its ability. "
            "I encourage you to also review your preferences on "
            '<a href="https://nusmods.com/courses?sem[0]=1&sem[1]=2&sem[2]=3&sem[3]=4" target="_blank" style="color:#FFD700;">NUSMods</a>!'
        )
        render_note(note)

st.markdown("""---""")

st.dataframe(
    user.filtered_data,
    use_container_width=True,
    height=500,
    hide_index=True,
    column_config=None)

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