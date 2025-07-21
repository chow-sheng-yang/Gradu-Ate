import json
from decimal import Decimal, ROUND_HALF_UP
import numpy as np
import pandas as pd

with open('track_requirements.json') as f:
    track_requirements = json.load(f)

#######################
# Helper Functions

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
            "S" : 0
        }
    return grade_point_mapping

def grade_point_mapper(grade):
    grade_mapping = get_grade_mapping()
    if grade in grade_mapping.keys():
        return grade_mapping[grade]
    return None
    
def get_track_requirements(track:str, type=None):
    if track.startswith('MINOR-'):
        return 20
    elif track.startswith('MAJOR-'):
        return 40
    else:
        return track_requirements[track][type]

def compute_cgpa(df):
    df = df[~(df['Grade'] == "S")]
    df = df.drop_duplicates(subset='Module_Code', keep='first')
    cgpa = np.sum(df['GPA'] * df['Units']) / sum(df['Units'])
    return cgpa

def round_half_up(series, decimals=2):
    return series.apply(lambda x: float(Decimal(str(x)).quantize(Decimal('1.' + '0'*decimals), rounding=ROUND_HALF_UP)))


# def render_spider_chart(df):

#     categories = df['Module_Type'].tolist()
#     values = df['avg_GPA'].tolist()

#     values += values[:1]
#     categories += categories[:1]

#     fig = go.Figure(
#         data=[
#             go.Scatterpolar(
#                 r=values,
#                 theta=categories,
#                 fill='toself',
#                 name='Average GPA',
#                 line=dict(color=scm_hex[2], width=2),
#                 fillcolor=hex_to_rgba(dba_hex[3], alpha=0.3)
#             )
#         ],
#         layout=go.Layout(
#             polar=dict(
#                 bgcolor='#0d1b2a',  # darker radial background
#                 radialaxis=dict(
#                     visible=True,
#                     range=[0, 5],
#                     tickfont=dict(size=20, color='#FFFFFF'),
#                     gridcolor='#444444',         # optional: dim gridlines
#                     linecolor='#888888'          # optional: dim axis line
#                 ),
#                 angularaxis=dict(
#                     tickfont=dict(size=16, color='#FFFFFF'),
#                     gridcolor='#444444'
#                 )
#             ),
#             showlegend=False,
#             width=400,
#             height=400,
#             margin=dict(l=20, r=20, t=20, b=20),
#             paper_bgcolor='rgba(13, 27, 42, 1)',   # transparent outer background
#             plot_bgcolor='rgba(13, 27, 42, 1)'
#         )
#     )

#     st.markdown("""
#         <h3 style='font-size: 38px; font-weight: 600; color: #FFFFFF; margin-bottom: 1rem;'>
#             Grade Distribution by Track
#         </h3>
#         """, unsafe_allow_html=True
#         )

#     st.plotly_chart(fig, use_container_width=True)


# def render_completion_table(df):

#     for _, row in df.iterrows():
#         module = row['Module_Type']
#         rate = row['Completion_Rate']

#         st.markdown(f"""
#         <div style="
#             margin-bottom: 1rem;
#             padding: 0.75rem 1rem;
#             background: #14243b;
#             border: 1px solid rgba(255, 255, 255, 0.15);
#             border-radius: 0.5rem;
#         ">
#             <strong style="color: #FFFFFF; font-size: 1.5rem; font-family: 'Arial', sans-serif;">{module}</strong>
#             <div style="
#                 margin-top: 0.4rem;
#                 height: 16px;
#                 background: #222;
#                 border-radius: 999px;
#                 overflow: hidden;
#             ">
#                 <div style="
#                     width: {rate}%;
#                     height: 100%;
#                     background: linear-gradient(90deg, #2d0d97, #970d48);
#                     transition: width 1s ease-in-out;
#                     box-shadow: 0 0 6px #00E0FF;
#                 "></div>
#             </div>
#             <p style="margin: 0.25rem 0 0; font-size: 0.85rem; color: #CCCCCC; font-family: 'Arial', sans-serif;">
#                 {rate:.2f}%
#             </p>
#         </div>
#         """, unsafe_allow_html=True)

# def render_completion_donut(completion_rate, label):

#     chart_color = ['#00E0FF', '#FF6E00']

#     source = pd.DataFrame({
#         "Label": ['', label],
#         "Value": [100 - completion_rate, completion_rate]
#     })
#     source_bg = pd.DataFrame({
#         "Label": ['', label],
#         "Value": [100, 0]
#     })

#     plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=80, cornerRadius=15).encode(
#         theta="Value:Q",
#         color=alt.Color("Label:N",
#                         scale=alt.Scale(domain=[label, ''], range=chart_color),
#                         legend=None)
#     ).properties(width=200, height=200)

#     plot = alt.Chart(source).mark_arc(innerRadius=80, cornerRadius=15).encode(
#         theta="Value:Q",
#         color=alt.Color("Label:N",
#                         scale=alt.Scale(domain=[label, ''], range=chart_color),
#                         legend=None)
#     ).properties(width=200, height=200)

#     text = alt.Chart(pd.DataFrame({'text': [f"{completion_rate:.1f}%"]})).mark_text(
#         font="Arial",
#         fontSize=28,
#         fontWeight="bold",
#         color="#FFFFFF"
#     ).encode(text='text:N')

#     donut_chart = plot_bg + plot + text

#     st.markdown(f"""
#     <div style="
#         background-color: #14243b;
#         padding: 0.5rem;
#         border-radius: 0.5rem;
#         box-shadow: 0 0 10px #00E0FF;
#         margin-bottom: 1rem;
#         display: flex;
#         flex-direction: column;
#         align-items: center;
#         font-family: 'Arial', sans-serif;
#     ">
#         <strong style="color: #FFFFFF; font-size: 1.05rem;">{label}</strong>
#     """, unsafe_allow_html=True)

#     st.altair_chart(donut_chart, use_container_width=True)

#     st.markdown("</div>", unsafe_allow_html=True)
    