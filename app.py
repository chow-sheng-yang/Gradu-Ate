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

from helper_functions import *
from grade_optimiser import GradeOptimizer
from user import User
from statsmodels.nonparametric.smoothers_lowess import lowess

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

# -- Colors:

dba_hex = [to_hex(c) for c in sns.color_palette('Blues', n_colors=4)]
scm_hex = [to_hex(c) for c in sns.color_palette('Oranges', n_colors=4)]

# -- Coloring Multi-Select Boxes:

st.markdown(f"""
    <style>
    /* Change background of selected options in multiselect */
    .stMultiSelect [data-baseweb="tag"] {{
        background-color: {dba_hex[3]} !important;
        color: white !important;
    }}
    </style>
""", unsafe_allow_html=True)

# -- Change Side Bar Color:

st.markdown(f"""
    <style>
        [data-testid="stSidebar"] {{
            background-color: #2e3b4e;
        }}
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
    <style>
    /* Make sidebar content a flex container and center vertically */
    [data-testid="stSidebar"] > div:first-child {
        height: 100vh;          /* Full viewport height */
        display: flex;
        flex-direction: column;
        justify-content: center; /* Vertical centering */
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
            background-color: {scm_hex[2]}20;
            border-left: 6px solid #{scm_hex[2]}];
            padding: 0.5rem;
            margin-top: 0.15rem;
            margin-bottom: 0.15rem;
            border-radius: 0.5rem;
            font-size: 0.95rem;
            color: #1a1a1a;
        ">
            <strong style="color:#f57f17;">⚠️ Note:</strong> {message}
        </div>
        """,
        unsafe_allow_html=True
    )
        
def render_metric_box(label, value:int, gradient_angle="135"):
    delta = +4
    st.markdown(
        f"""
        <div style="
            background: linear-gradient({gradient_angle}deg, #cc5500, #e77a70);
            border-radius: 1rem;
            width: 300px;
            height: 260px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            font-family: 'Arial', sans-serif;
            margin-bottom: 1rem;
        ">
            <div style="font-size: 1.50rem; color: #FFFFFF; font-weight: 600;">{label}</div>
            <div style="font-size: 4rem; font-weight: 500; color: #FFFFFF; margin: 0.5rem 0;">{value}</div>
            <div style="font-size: 1.25rem; font-weight: 400; color: #00FF00;">
                {'▲' if delta > 0 else '▼' if delta < 0 else ''} {abs(delta) if delta != 0 else ''}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_st_white_card(label):
    st.markdown(f"""
    <div style="
        margin-bottom: 1rem;
        padding: 0.75rem 1rem;
        background: #fff;
        border-radius: 0.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        font-size: 1.25rem;
        color: #2a2a2a;
    ">
        {label}
    </div>
    """, unsafe_allow_html=True)

def render_completion_table(df):

    for _, row in df.iterrows():
        module = row['Module_Type']
        rate = row['Completion_Rate']

        st.markdown(f"""
        <div style="
            margin-bottom: 1rem;
            padding: 0.75rem 1rem;
            background: #14243b;
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 0.5rem;
            box-shadow: 0 2px 10px rgba(255,255,255,0.05);
        ">
            <strong style="color: #FFFFFF; font-size: 1.5rem;">{module}</strong>
            <div style="
                margin-top: 0.4rem;
                height: 16px;
                background: #333333;
                border-radius: 999px;
                overflow: hidden;
            ">
                <div style="
                    width: {rate}%;
                    height: 100%;
                    background: linear-gradient(90deg, {dba_hex[3]}, {scm_hex[3]});
                    transition: width 1s ease-in-out;
                "></div>
            </div>
            <p style="margin: 0.25rem 0 0; font-size: 0.85rem; color: #DDDDDD;">
                {rate:.2f}%
            </p>
        </div>
        """, unsafe_allow_html=True)

def render_spider_chart(df):

    categories = df['Module_Type'].tolist()
    values = df['avg_GPA'].tolist()

    values += values[:1]
    categories += categories[:1]

    fig = go.Figure(
        data=[
            go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Average GPA',
                line=dict(color=scm_hex[2], width=2),
                fillcolor=hex_to_rgba(dba_hex[3], alpha=0.3)
            )
        ],
        layout=go.Layout(
            polar=dict(
                bgcolor='#0d1b2a',  # darker radial background
                radialaxis=dict(
                    visible=True,
                    range=[0, 5],
                    tickfont=dict(size=20, color='#FFFFFF'),
                    gridcolor='#444444',         # optional: dim gridlines
                    linecolor='#888888'          # optional: dim axis line
                ),
                angularaxis=dict(
                    tickfont=dict(size=16, color='#FFFFFF'),
                    gridcolor='#444444'
                )
            ),
            showlegend=False,
            width=400,
            height=400,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='rgba(13, 27, 42, 1)',   # transparent outer background
            plot_bgcolor='rgba(13, 27, 42, 1)'
        )
    )

    st.markdown("""
        <h3 style='font-size: 38px; font-weight: 600; color: #FFFFFF; margin-bottom: 1rem;'>
            Grade Distribution by Track
        </h3>
        """, unsafe_allow_html=True
        )

    st.plotly_chart(fig, use_container_width=True)

def render_bar_chart(df):

    df = df.sort_values(by='avg_GPA', ascending=True)

    # Plotly gradient bar simulation
    fig = go.Figure()

    fig.add_trace(go.Bar(
    x=df['avg_GPA'],
    y=df['Module_Type'],
    orientation='h',
    marker=dict(
        color='rgba(0,123,255,0.7)',
        line=dict(color='rgba(0,123,255,1.0)', width=1.5)
    ),
    text=df['avg_GPA'].round(2),
    textposition='outside',
    hovertemplate='<b>%{y}</b><br>CGPA: %{x:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title=dict(
            text="GPA Distribution by Track",
            font=dict(size=40, color="white"),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(title='Average GPA', range=[min(df['avg_GPA'])-0.05, 5.0], tickfont=dict(size=14)),
        yaxis=dict(title='Track', tickfont=dict(size=14)),
        height=500,
        margin=dict(l=60, r=40, t=120, b=40),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor=hex_to_rgba('#14243b', 0.98),
        showlegend=False,
        bargap=0.5
    )

    st.plotly_chart(fig, use_container_width=True)
    
def render_completion_donut(completion_rate, label):

    chart_color = [dba_hex[3], dba_hex[1]]

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
    ).properties(width=260, height=260)

    plot = alt.Chart(source).mark_arc(innerRadius=80, cornerRadius=15).encode(
        theta="Value:Q",
        color=alt.Color("Label:N",
                        scale=alt.Scale(domain=[label, ''], range=chart_color),
                        legend=None)
    ).properties(width=260, height=260)

    text = alt.Chart(pd.DataFrame({'text': [f"{completion_rate:.1f}%"]})).mark_text(
        font="sans-serif",
        fontSize=28,
        fontWeight="bold",
        color="#FFFFFF"
    ).encode(text='text:N')
    donut_chart = plot_bg + plot + text

    st.markdown(f"""
    <div style="
        background-color: white;
        padding: 1.25rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
        align-items: center;
    ">
        <strong style="color: #2a2a2a; font-size: 1.05rem;">{label}</strong>
    """, unsafe_allow_html=True)

    st.altair_chart(donut_chart, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)
    
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

   # ==== Waterfall Chart ====
    fig.add_trace(go.Waterfall(
        x=plot_df['Term'],
        y=plot_df['CGPA_Delta'],
        measure=plot_df['Measure'],
        connector={"line": {"color": "rgba(63, 63, 63, 0.5)"}},
        text=plot_df['CGPA_Delta'].map("{:.2f}".format),
        textposition="outside",
        textfont=dict(size=16, family='Arial'),
        increasing=dict(marker=dict(color=dba_hex[3])),   # for increases
        decreasing=dict(marker=dict(color=scm_hex[3])),   # for decreases
        totals=dict(marker=dict(color=dba_hex[3]))
    ))

    fig.add_trace(go.Scatter(
    x=plot_df['Term'],
    y=plot_df['CGPA'],
    mode='lines',
    line=dict(color='rgba(0,123,255,1)', width=3, shape='spline'),
    name='CGPA Trend'
    ))

    # Add layered fills to simulate vertical gradient
    for i, alpha in enumerate([0.20, 0.17, 0.14, 0.11, 0.08, 0.05, 0.03, 0.01, 0.008, 0.006, 0.004, 0.002, 0.001]):
        y_offset = plot_df['CGPA'] - (i + 1) * 0.04  # Each layer slightly below the previous
        fig.add_trace(go.Scatter(
            x=plot_df['Term'],
            y=y_offset,
            mode='lines',
            line=dict(width=0),
            fill='tonexty',
            fillcolor=f'rgba(0,123,255,{alpha})',
            hoverinfo='skip',
            showlegend=False
        ))
    # ==== Layout ====
    fig.update_layout(
        title=dict(
            text="CGPA Change Over Semesters",
            font=dict(size=40, color="white"),
            x=0.5,
            xanchor='center'
        ),
        yaxis_title="CGPA",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor=hex_to_rgba('#14243b', 0.98),
        xaxis=dict(showgrid=False, tickfont=dict(size=20)),
        yaxis=dict(range=[3.9, 4.8], showgrid=False, tickfont=dict(size=20)),
        height=500,
        margin=dict(l=40, r=40, t=120, b=40),
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)

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
        # df_no_dup = df_not_year_long.drop_duplicates(subset='Module_Code', keep='first')

        df = pd.concat([df_year_long, df_not_year_long], ignore_index=True)

# -- Side Bar Title:

    st.markdown("# 🎓 NUS Dashboard")

# -- User Configuration:

    user = User(raw_data=df)

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
    
# # -- Select Double-Counted Modules:
#     double_counted_options = set([module for module in df['Module_Code'] if \
#                               (df[df['Module_Code'] == module].shape[0] > 1) and \
#                               (df[df['Module_Code'] == module]['Units'].sum() > 4)])
#     double_counted_mods = st.multiselect('Select the Modules you are Double-Counting::', 
#                             options=double_counted_options,
#                             default=None)


# -- Input Text Message for Module Recommendation:
    
    modrec_input = st.text_input("Based on your Main Specialisation, describe areas of interest for Module Recommendation:")
    



# -- Filtering Process:

    user.set_main_track(main_track)
    # user.set_double_counts(double_counted_mods)
    user.apply_filter(selected_tracks)

    if user.get_filtered_data() is None or user.get_filtered_data().empty:
        st.warning("No data available based on the current filter settings!")
        st.stop()

# -- Note Card:

    note = "Tracks that are not CORE, GE, HONS or Main Specialisation will count to UEs!"
    render_note(note)

#######################
# Main Page

top_col1, top_col2 = st.columns([2, 1], gap='medium')

# -- Top Metrics:

completion_rate = user.snapshot.completion_rate
completion_rate = min(completion_rate, 100)

with top_col1:
    st.markdown("""
        <h3 style='font-size: 38px; font-weight: 600; color: #FFFFFF; margin-bottom: 1rem;'>
           Overall Academic Metrics
        </h3>
        """, unsafe_allow_html=True
        )
    box1, box2, box3, box4 = st.columns(4, gap='small')
    with box1:
        render_metric_box(label='Total MCs', value=user.snapshot.total_units, gradient_angle=135)
    with box2:
        render_metric_box(label='Cumulative GPA', value=user.snapshot.cgpa, gradient_angle=120)
    with box3:
        render_metric_box(label='Remaining S/Us', value= (32 - (user.snapshot.SU_used * 4)), gradient_angle=150)
    with box4:
        render_metric_box(label='Year of Study', value= user.snapshot.current_year, gradient_angle=160)

with top_col2:
        render_completion_donut(
            completion_rate=completion_rate, 
            label=f"⏳ You are left with {4 - user.snapshot.current_year} year(s) to go!",
    )

st.markdown("""---""")

# -- Bottom Side Panel:
col1, col2 = st.columns((0.25, 0.75), gap='medium')

with col1:

    st.markdown("""
        <h3 style='font-size: 38px; font-weight: 600; color: #FFFFFF; margin-bottom: 1rem;'>
           Individual Track Analysis
        </h3>
        """, unsafe_allow_html=True
    )
    completion_status, remaining_status = user.snapshot.track_completion_df, user.snapshot.track_remaining
    render_completion_table(completion_status)
    for track, status in remaining_status:
            if status:
                with st.expander(f"📘 {track} - Click to view outstanding requirements"):
                    st.markdown(
                        f"""
                        <div style="
                            background-color: #FFFFFF;
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

# -- Bottom Middle Panel:

with col2:

    table_col1, table_col2 = st.columns(2)

    with table_col1:
       
       st.markdown("""
        <h3 style='font-size: 38px; font-weight: 600; color: #FFFFFF; margin-bottom: 1rem;'>
            Grades Analysis
        </h3>
        """, unsafe_allow_html=True
    )
       
       render_waterfall_chart(df=user.filtered_data)

       track_gpas = user.filtered_data.groupby('Module_Type').agg(avg_GPA=('GPA', np.mean)).reset_index()
       render_bar_chart(track_gpas)

# -- Bottom Right Panel:

    with table_col2:
        pass
        

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