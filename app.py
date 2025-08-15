import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from matplotlib.colors import to_hex
import streamlit as st
import streamlit.components.v1 as components
from utils import *
from theme import *
from user import User

#######################
# Page configuration

st.set_page_config(
    page_title="Your NUS BBA Dashboard",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded")

style_transition_buttons()
    
# -- Color/Size Parameter Configurations:

title_font_size_px = 25
title_font_size_rem = px_to_rem(title_font_size_px)
subtitle_font_size_px = title_font_size_px / 1.1
subtitle_font_size_rem = px_to_rem(subtitle_font_size_px)

top_padding_px, left_padding_px, right_padding_px, bottom_padding_px = 100, 100, 100, 100
top_padding_rem, left_padding_rem, right_padding_rem, bottom_padding_rem = px_to_rem(top_padding_px), px_to_rem(left_padding_px), px_to_rem(right_padding_px), px_to_rem(bottom_padding_px)

title_x_orient, title_y_orient = 0.05, 0.95

x_axis_tick_size_px, y_axis_tick_size_px = 18, 18
x_axis_tick_size_rem, y_axis_tick_size_rem = px_to_rem(x_axis_tick_size_px), px_to_rem(y_axis_tick_size_px)

delta_green = "#11c921"
delta_red = "#FF5555"

border_radius_px = 40
border_radius_rem = px_to_rem(40)

#######################
# Read Helper Data

electives_ranking = load_bba_electives_ranking()
electives_demand_vacancy = load_bba_electives_demand_vacancy_data()

#######################
# Functions to Render Charts/Visualisations/Widgets

def render_CGPA_box(label, sublabel, value:int, bg_color="#fa4202", text_color="#ffffff"):

    delta = round(user.snapshot.cgpa - user.init_cgpa, 2)

    if delta >= 0:
        delta_symbol = '+'
        delta_color = delta_green 
        delta_msg = f"{abs(delta)} from {user.init_cgpa}"
    else:
        delta_symbol = '-'
        delta_color = delta_red
        delta_msg = f"{abs(delta)} from {user.init_cgpa}"

    delta_display = f"{delta_symbol} {delta_msg}"

    degree_class = degree_classifier(user.snapshot.cgpa)

    st.markdown(f"""
        <div style="
            background: {bg_color};
            border-radius: 40px;
            width: 550px;
            height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            font-family: 'Inter', sans-serif;
            margin-bottom: 1rem;
            border: 3px solid {colors.chart_background_color};
            padding: 1.5rem 2rem;
            color: {text_color};
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        ">
            <div style="
                display: flex;
                flex-direction: row;
                justify-content: space-between;
                align-items: flex-start;
                height: 100%;
            ">
                <div style="
                    display: flex;
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 0.4rem;
                ">
                    <div style="
                        font-size: {subtitle_font_size_rem}rem;
                        font-weight: 500;
                        color: {text_color};
                    ">
                        {label}
                    </div>
                    <div style="
                        font-size: 4.5rem;
                        font-weight: 500;
                        color: {text_color};
                        line-height: 1;
                    ">
                        {value}
                    </div>
                    <div style="
                        font-size: {subtitle_font_size_rem}rem;
                        font-weight: 500;
                        color: {text_color};
                    ">
                        {sublabel}
                    </div>
            </div>
            <div style="
                display: flex;
                flex-direction: column;
                align-items: flex-end;
                gap: 0.5rem;
            ">
                <div style="
                    background-color: white;
                    color: {delta_color};
                    padding: 6px 14px;
                    border-radius: {border_radius_px}px;
                    font-size: {x_axis_tick_size_rem}rem;
                    font-weight: 800;
                    box-shadow: 0 0 4px {delta_color}55;
                    white-space: nowrap;
                ">
                    {delta_display}
                </div>
                <div style="
                    color: {text_color};
                    padding: 6px 0px;
                    border-radius: 999px;
                    font-size: {x_axis_tick_size_rem}rem;
                    font-weight: 500;
                    white-space: nowrap;
                ">
                    {degree_class}
                </div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)    

def render_metric_box(label, sublabel, value:int, icon, bg_color, text_color, subtext_color):

    st.markdown(f"""
        <div style="
            background: {bg_color};
            border-radius: 40px;
            width: 550px;
            height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            font-family: 'Inter', sans-serif;
            margin-bottom: 1rem;
            border: 3px solid {colors.chart_background_color};
            padding: 1.5rem 2rem;
            color: {text_color};
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        ">
            <div style="
                display: flex;
                flex-direction: row;
                justify-content: space-between;
                align-items: flex-start;
                height: 100%;
            ">
                <div style="
                    display: flex;
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 0.4rem;
                ">
                    <div style="
                        font-size: {subtitle_font_size_rem}rem;
                        font-weight: 400;
                        color: {text_color};
                    ">
                        {label}
                    </div>
                    <div style="
                        font-size: 4.5rem;
                        font-weight: 500;
                        color: {text_color};
                        line-height: 1;
                    ">
                        {value}
                    </div>
                    <div style="
                        font-size: {subtitle_font_size_rem}rem;
                        font-weight: 400;
                        color: {subtext_color};
                    ">
                        {sublabel}
                    </div>
                </div>
                <div style="
                    width: 64px;       /* adjust size */
                    height: 64px;
                    align-self: flex-start;
                ">
                    <img src="data:image/jpeg;base64,{icon}"
                    style="transform: scale(1.5) translateX(-20%) translateY(-20%); transform-origin: top left;" />
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_degree_completion_donut(completion_rate):

    fig = go.Figure()

    # Base Ring (Remaining)
    fig.add_trace(go.Pie(
        values=[completion_rate, 100 - completion_rate],
        labels=['', 'Remaining'],
        hole=0.85,
        marker=dict(colors=["rgba(0, 0, 0, 0)", colors.secondary_chart_color]),
        textinfo='none',
        showlegend=False,
        sort=False,
        pull=[0, 0.1]
    ))

    # Main Ring (Completed)
    fig.add_trace(go.Pie(
        values=[completion_rate, 100 - completion_rate],
        labels=['Completed', 'Remaining'],
        hole=0.6,
        marker=dict(colors=[colors.primary_chart_color, "rgba(0, 0, 0, 0)"]),
        textinfo='none',
        showlegend=False,
        sort=False,
        pull=[0, 0]
    ))

    # Dummy Trace for Legend Display
    fig.add_trace(go.Pie(
        values=[1, 1],
        labels=['Completed', 'Remaining'],
        marker=dict(colors=[colors.primary_chart_color, colors.secondary_chart_color]),
        textinfo='none',
        hoverinfo='skip',
        showlegend=True,
        hole=1, 
        sort=False,
        opacity=1,
        visible=True
    ))

    fig.update_layout(
        annotations=[
            dict(
                text=f"<b>{completion_rate:.0f}</b><span style='font-size:30%;'>%</span>",  # smaller % sign
                x=0.5,
                y=0.5,
                font=dict(size=100, color=colors.primary_text_color, family="Inter, sans-serif"),
                showarrow=False,
                xref='paper',
                yref='paper',
                align='center',
                valign='middle'
            ),
        ],
        title=dict(
            text="🎓 Degree Completion (%)",
            font=dict(size=title_font_size_px, color=colors.primary_text_color, family="Inter, sans-serif"),
            x=title_x_orient,                  # Left-align
            xanchor='left',
            y=title_y_orient,                  # Higher than subtitle
            yanchor='top'
        ),
        legend=dict(
            font=dict(color=colors.secondary_text_color, size=subtitle_font_size_px),
            x=0.5,
            y=-0.1,
            orientation='h',
            xanchor='center',
            yanchor='top',
            bgcolor='rgba(0,0,0,0)'  # transparent background
        ),
        width=100,             # Shrink entire chart width
        height=600,
        margin=dict(l=left_padding_px, r=right_padding_px, t=top_padding_px, b=bottom_padding_px),
        plot_bgcolor=colors.chart_background_color,
        paper_bgcolor=colors.chart_background_color
    )

    st.plotly_chart(fig, use_container_width=True)

def render_track_progress_donut(df):

    df = df.sort_values(by='Completion_Rate')

    fig = go.Figure()

    num_tracks = len(df)
    inner_radius = 0.1
    outer_radius = 1.0
    ring_thickness = (outer_radius - inner_radius) / num_tracks

    # Precompute hole sizes for each ring
    hole_sizes = []
    for i in range(num_tracks):
        hole = inner_radius + i * ring_thickness
        if hole + ring_thickness > outer_radius:
            hole = outer_radius - ring_thickness
        hole_sizes.append(round(hole, 4))

    # Add each donut ring for each track
    custom_legend_items = []
    for i, (_, row) in enumerate(df.iterrows()):
        completed = row['Completion_Rate']
        remaining = 1 - completed

        # Color logic
        ring_color = (
            colors.primary_chart_color if completed == 1 else
            colors.secondary_chart_color if completed >= 0.5 else
            colors.secondary_text_color if completed > 0 else "#141518"
        )

        # Add trace for the ring
        fig.add_trace(go.Pie(
            values=[completed, remaining],
            labels=[f"{row['Module_Type']} ({int(completed * 100)}%)", 0],
            name=row['Module_Type'],
            hole=hole_sizes[i],
            sort=False,
            direction='clockwise',
            marker=dict(
                colors=[ring_color, colors.chart_background_color],
                line=dict(color=colors.chart_background_color, width=5)
            ),
            textinfo='none',
            showlegend=False,  # <- Enable legend
            hovertemplate=f"<b>{row['Module_Type']}</b><br>Completion: {completed*100:.1f}%<extra></extra>"
        ))

        # Custom legend item as annotation
        custom_legend_items.append(
            dict(
                x=1.2,
                y=0.9 - i * 0.15,
                xref='paper',
                yref='paper',
                showarrow=False,
                align="left",
                text=(
                    f"<span style='display:inline-block; width:12px; height:12px; background-color:{colors.primary_chart_color};"
                    f"border-radius:3px; margin-right:8px;'></span>"
                    f"<span style='font-size:{subtitle_font_size_px}px; color:{colors.secondary_text_color};'>"
                    f"<b>{row['Module_Type']}</b>: {int(completed * 100)}%</span>"
                ),
                bgcolor="rgba(0,0,0,0)",
                opacity=1
            )
        )

    # Layout
    fig.update_layout(
        annotations=custom_legend_items,
        title=dict(
            text="🗂️ What You Have Completed",
            font=dict(size=title_font_size_px, color=colors.primary_text_color, family="Inter, sans-serif"),
            x=title_x_orient,
            xanchor='left',
            y=title_y_orient,
            yanchor='top'
        ),
        height=600,
        width=750,
        margin=dict(l=left_padding_px-100, r=right_padding_px+100, t=top_padding_px+20, b=bottom_padding_px+20),
        paper_bgcolor=colors.chart_background_color,
        plot_bgcolor=colors.chart_background_color
    )

    st.plotly_chart(fig, use_container_width=True)

def render_track_gpa_barchart(df):

    df = df[['Module_Type', 'CGPA']]
    df = df.sort_values(by='CGPA', ascending=True)

    fig = go.Figure()

    # Background bar & half-circle markers at right edge to simulate rounded edges
    fig.add_trace(go.Bar(
        y=df['Module_Type'],
        x=[5] * len(df),
        orientation='h',
        marker=dict(
            color=colors.app_bgcolor,
            line=dict(color=colors.app_bgcolor)
        ),
        hoverinfo='skip',
        opacity=1.0,
        name='Max GPA',
        showlegend=False
    ))

    fig.add_trace(go.Bar(
        y=df['Module_Type'],
        x=df['CGPA'],
        orientation='h',
        marker=dict(color=[
            colors.primary_chart_color if val >= user.snapshot.cgpa else colors.secondary_chart_color
            for val in df['CGPA']
            ]
        ),
        hovertemplate='Cumulative GPA: %{x}<extra></extra>',
        name='Cumulative GPA',
        showlegend=False
    ))

    # Add invisible dummy traces for legend
    fig.add_trace(go.Bar(
        x=[None],
        y=[None],
        marker=dict(color=colors.primary_chart_color),
        name=f'>=  {user.snapshot.cgpa}',
        hoverinfo='skip',
        showlegend=True
    ))

    fig.add_trace(go.Bar(
        x=[None],
        y=[None],
        marker=dict(color=colors.secondary_chart_color),
        name=f'<  {user.snapshot.cgpa}',
        hoverinfo='skip',
        showlegend=True
    ))

    # Layout styling
    fig.update_layout(
        barmode='overlay',
        bargap=0.5,  # Higher value = thinner bars visually
        title=dict(
            text="📊 Your CGPA per Track",
            font=dict(size=title_font_size_px, color=colors.primary_text_color, family="Inter, sans-serif"),
            x=title_x_orient,                  # Left-align
            xanchor='left',
            y=title_y_orient-0.05,                  # Higher than subtitle
            yanchor='top'
        ),
        xaxis=dict(
            title=dict(text='Cumulative GPA', font=dict(size=x_axis_tick_size_px, color=colors.secondary_text_color)),
            range=[min(df['CGPA']) - 0.05, 5.05],
            tickfont=dict(size=x_axis_tick_size_px, color=colors.secondary_text_color),
            showgrid=False
        ),
        yaxis=dict(
            tickfont=dict(size=y_axis_tick_size_px, color=colors.secondary_text_color),
            showgrid=False
        ),
        legend=dict(
            x=1.05, y=1.05,
            xanchor='left', yanchor='top',
            font=dict(
                size=subtitle_font_size_px,  # Optional: set size
                color=colors.secondary_text_color         # 👈 Your desired color (e.g., "#CCCCCC")
            ),
            bgcolor='rgba(0,0,0,0)',         # Optional: make background transparent
            borderwidth=0                   # Optional: remove border
        ),
        height=440,
        margin=dict(l=left_padding_px+50, r=right_padding_px+50, t=top_padding_px, b=bottom_padding_px),
        plot_bgcolor=colors.chart_background_color,
        paper_bgcolor=colors.chart_background_color,
        showlegend=True
    )

    # Now display the chart normally
    st.plotly_chart(fig, use_container_width=True)

def render_cgpa_trend_waterfallchart(df):

    def pad_missing_lists(year_list, cgpa_list, measure_list):

        full_term_order = [11, 12, 21, 22, 31, 32, 41, 42, 51, 52]
        max_term = max(year_list)
        padded_terms = [term for term in full_term_order if term <= max_term]
        term_cgpa_map = dict(zip(year_list, cgpa_list))
        term_measure_map = dict(zip(year_list, measure_list))

        padded_cgpas = []
        last_cgpa = 0
        for term in padded_terms:
            if term in term_cgpa_map:
                cgpa = term_cgpa_map[term]
                padded_cgpas.append(cgpa)
                last_cgpa = cgpa
            else:
                padded_cgpas.append(last_cgpa)
        # padded_cgpas = [term_cgpa_map.get(term, 0) for term in padded_terms]

        padded_measures = [term_measure_map.get(term, "relative") for term in padded_terms]
        return padded_cgpas, padded_terms, padded_measures

    cgpa_vector, measure_vector, year_vector = [], [], []

    for term in sorted(df['Term'].unique()):

        data = df[df['Term'] <= term]

        cgpa = user.compute_cgpa(data)
    
        cgpa_vector.append(cgpa)

        if term == min(df['Term']):
            measure_vector.append('absolute')
        else:
            measure_vector.append('relative')
        
        # term = str(term)
        year_vector.append(term)

    padded_cgpas, padded_terms, padded_measures = pad_missing_lists(year_list=year_vector,
                                                                    cgpa_list=cgpa_vector,
                                                                    measure_list=measure_vector)

    padded_cgpas_vector = pd.Series(padded_cgpas).apply(lambda x : round_half_up(x))

    padded_change_vector = padded_cgpas_vector.diff()
    padded_change_vector.iloc[0] = padded_cgpas_vector.iloc[0]
    padded_change_vector = padded_change_vector.fillna(0)

    padded_terms = [str(term) for term in padded_terms]
    padded_terms = [f"Y{term[0]}S{term[1]}" for term in padded_terms]

    plot_df = pd.DataFrame({
        'Term': padded_terms,
        'CGPA': padded_cgpas_vector,
        'CGPA_Delta' : padded_change_vector,
        'Measure' : padded_measures
    })

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=plot_df['Term'],
        y=plot_df['CGPA'],
        mode='lines+markers',
        line=dict(color=colors.primary_chart_color, width=3, shape='spline'),
        marker=dict(size=9, color=colors.primary_chart_color),
        name='CGPA Trend',
        fill='tozeroy',
        fillcolor=hex_to_rgba(colors.primary_chart_color, alpha=0.1)
    ))

    # Add delta annotations
    for i, (x, delta) in enumerate(zip(plot_df['Term'], plot_df['CGPA_Delta'])):

        delta_color = delta_green if delta >= 0 else delta_red

        fig.add_annotation(
            x=x,
            y=plot_df['CGPA'].iloc[i] + 0.1,  # position above point
            text=f"{delta:+.2f}",
            showarrow=False,
            font=dict(size=16, color=delta_color, family='Inter, sans-serif'),
            borderwidth=1,
            borderpad=4
        )

    # Layout
    fig.update_layout(
        title=dict(
            text="📈 Your CGPA Over Time",
            font=dict(size=title_font_size_px, color=colors.primary_text_color, family="Inter, sans-serif"),
            x=title_x_orient,                  
            xanchor='left',
            y=title_y_orient-0.05,                 
            yanchor='top'
        ),
        plot_bgcolor=colors.chart_background_color,
        paper_bgcolor=colors.chart_background_color,
        xaxis=dict(
            showgrid=False,
            tickfont=dict(size=x_axis_tick_size_px, color=colors.secondary_text_color),
            title=dict(text='Academic Term', font=dict(size=x_axis_tick_size_px, color=colors.secondary_text_color))
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(size=y_axis_tick_size_px, color=colors.secondary_text_color),
            title=dict(text='Cumulative GPA', font=dict(size=y_axis_tick_size_px, color=colors.secondary_text_color)),
            range=[-1, max(padded_cgpas_vector)+0.2] if (min(padded_cgpas_vector) == 0) else [min(padded_cgpas_vector)-0.2, max(padded_cgpas_vector)+0.2]
        ),
        legend=dict(
            font=dict(size=subtitle_font_size_px, color=colors.secondary_text_color),
            x=0.85,
            y=title_y_orient+0.35,
            xanchor='left',
            yanchor='top',
            bgcolor='rgba(0,0,0,0)'
        ),
        height=440,
        margin=dict(l=left_padding_px, r=right_padding_px, t=top_padding_px, b=bottom_padding_px),
        showlegend=True
    )
 
    st.plotly_chart(fig, use_container_width=True)

def render_demand_vacancy_trends(elective_df: pd.DataFrame, demand_df: pd.DataFrame, top_modules: set):

    term_order = ["AY20-21-Sem-2",
                  "AY20-21-Special-Term-2",
                  "AY21-22-Sem-1", 
                  "AY21-22-Sem-2", 
                  "AY22-23-Sem-1",
                  "AY22-23-Sem-2",
                  "AY23-24-Sem-1",
                  "AY23-24-Sem-2",
                  "AY23-24-Special-Term-1",
                  "AY24-25-Sem-1",
                  "AY24-25-Sem-2",
                  "AY25-26-Sem-1"]
    
    term_order = [term for term in term_order if term in set(demand_df['Academic_Term'].unique())]

    # Filter to only top 3 modules
    demand_df = demand_df[demand_df['Module_Code'].isin(top_modules)].copy()
    elective_df = elective_df[elective_df['Module_Code'].isin(top_modules)].copy()

    # Order the x-axis
    demand_df['Academic_Term'] = pd.Categorical(demand_df['Academic_Term'], categories=term_order, ordered=True)

    # Sort for consistent plotting
    demand_df.sort_values(by=['Academic_Term', 'Module_Code'], inplace=True)

    # Create figure with 2 rows
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.4, 0.6]
    )

    color_map = [colors.primary_chart_color, colors.secondary_chart_color, colors.secondary_text_color]  # You can customize this
    module_colors = {mod: color_map[i] for i, mod in enumerate(top_modules)}

    # Line Chart for Demand
    for module in top_modules:
        df_mod = demand_df[demand_df['Module_Code'] == module]
        fig.add_trace(go.Scatter(
            x=df_mod['Academic_Term'],
            y=df_mod['Demand'],
            mode='lines+markers',
            name=f"{module} Demand",
            line=dict(shape='spline', color=module_colors[module], width=3),
            marker=dict(size=10),
            hovertemplate=f"<b>{module}</b><br>Term: %{{x}}<br>Demand: %{{y}}<extra></extra>",
            fill='tozeroy',
            fillcolor=hex_to_rgba(module_colors[module], alpha=0.05)
        ), row=2, col=1)

    # Add popularity score blocks as horizontal annotations
    positions = [0, 0.25, 0.73] 
    y_pos = 0.95

    for i, module in enumerate(top_modules):
        pop_score = elective_df.loc[elective_df['Module_Code'] == module, 'rank'].values[0]
        score_text = f"{pop_score:.2f}"

        fig.add_annotation(
            x=positions[i],
            y=y_pos,
            xref='paper',
            yref='paper',
            text=(
                f"<span style='font-size:{title_font_size_px}px; color: {colors.primary_text_color};'>{module}</span><br>"
                f"<br>"
                f"<span style='font-size:{subtitle_font_size_px-3}px; color:{colors.secondary_text_color};'>Ranking Score:</span><br>"
                f"<br><br><br><br>"
                f"<span style='font-size:70px; font-weight:bold; color:{module_colors[module]}; display:inline-block;'>{score_text}</span>"
                f"<span style='font-size:30px; color: {colors.secondary_text_color}'> /5</span></span>"
            ),
            showarrow=False,
            align='center',
            font=dict(size=14, color="#000000", family="Inter, sans-serif"),
            borderpad=8,
            bgcolor=colors.chart_background_color,
            opacity=0.9
        )
    
    # Subtext beside popularity scores
    fig.add_annotation(
        x=1.08,
        y=y_pos,
        xref='paper',
        yref='paper',
        text=(
            f"<span style='font-size:{subtitle_font_size_px-2}px; color:{colors.secondary_text_color};'>"
            f"<b>How Is Ranking Calculated?</b><br><br><br>"
            f"<span style='font-size:{subtitle_font_size_px-7}px; color:{colors.secondary_text_color};'>"
            f"<span style='color:{colors.secondary_chart_color};'>●</span> Demand to Vacancy Ratio<br><br>"
            f"<span style='color:{colors.secondary_chart_color};'>●</span> Oversubscription Trend<br><br>"
            f"<span style='color:{colors.secondary_chart_color};'>●</span> Demand Trend<br><br>"
            f"<span style='color:{colors.secondary_chart_color};'>●</span> Demand Inconsistency over<br>Semesters</i>"
            f"</span>"
        ),
        showarrow=False,
        align='left',
        borderpad=4,
        opacity=1
    )

   # Layout

    fig.update_xaxes(
        tickfont=dict(size=x_axis_tick_size_px, color=colors.secondary_text_color),
        showgrid=False,
        showticklabels=True,
        categoryorder='array',
        categoryarray=term_order,
        row=2,
        col=1
    )

    fig.update_yaxes(
        title=dict(text='Demand', font=dict(size=y_axis_tick_size_px, color=colors.secondary_text_color)),
        tickfont=dict(size=y_axis_tick_size_px, color=colors.secondary_text_color),
        showgrid=False,
        row=2,
        col=1
    )

    fig.update_layout(
        height=920,
        margin=dict(t=top_padding_px, l=left_padding_px, r=right_padding_px, b=bottom_padding_px+50),  # Extra bottom space for annotations
        title=dict(
            text="🗂️ Recommended Modules for Your Main Major" if user.main_major is not None else "🗂️ Modules with High Popularity Scores",
            font=dict(size=title_font_size_px, color=colors.primary_text_color, family="Inter, sans-serif"),
            x=title_x_orient,
            xanchor='left',
            y=title_y_orient,
            yanchor='top'
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=0.55,
            xanchor='left',
            x=0.5,
            font=dict(size=x_axis_tick_size_px, color=colors.secondary_text_color),
            bgcolor='rgba(0,0,0,0)'
        ),
        plot_bgcolor=colors.chart_background_color,
        paper_bgcolor=colors.chart_background_color,
        font=dict(color=colors.secondary_text_color),
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)

def render_table(df):

    # Color mapping function for Completion_Rate
    def get_completion_color(rate_percent):
        if rate_percent == 100:
            return delta_green
        elif rate_percent >= 50:
            return colors.primary_chart_color
        elif rate_percent > 0:
            return colors.secondary_chart_color
        else:
            return "#888888"

    styled_df = df[['Module_Type', 'Completion_Rate', 'Completion_Status']].copy()
    styled_df = styled_df.sort_values(by='Completion_Rate', ascending=False)

    # Convert Completion_Rate from decimal to % string and apply chip styling
    styled_df["Completion_Rate"] = styled_df["Completion_Rate"].apply(lambda rate: 
        f'<span class="grade-chip" style="background-color:{hex_to_rgba(get_completion_color(rate * 100), 1)};">{int(rate * 100)}%</span>'
    )

    # Format Completion_Status lists into HTML with line breaks
    styled_df["Completion_Status"] = styled_df["Completion_Status"].apply(
        lambda items: "<br>".join(items) if isinstance(items, list) else str(items)
    )
    
    # Rename Columns
    styled_df.columns = ['Track', 'Completion Rate', 'What You Need To Complete']

    # Build HTML content
    html = f"""
    <div class="table-wrapper">
        {styled_df.to_html(classes="styled-table", escape=False, index=False)}
    </div>
    """

    # Final HTML + CSS
    html_string = f"""
    <style>
        .table-wrapper {{
            background-color: {colors.chart_background_color};
            border-radius: 60px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            padding: 1rem;
            width: fit-content;
            margin: auto;
            max-height: 700px;
            overflow-y: auto;
            margin: auto;
        }}

        .styled-table {{
            border-collapse: collapse;
            width: 100%;
            table-layout: fixed;
            font-family: 'Inter', sans-serif;
            font-size: {subtitle_font_size_rem}rem;
            color: {colors.secondary_text_color};
            background-color: {colors.chart_background_color};
            border-radius: 60px;
            border: none;
        }}

        .styled-table thead tr {{
            background-color: {colors.chart_background_color};
            color: {colors.primary_text_color};
            font-weight: 700;
            font-size: {title_font_size_rem}rem;
        }}

        .styled-table thead th {{
            text-align: center;
            border: none;
            padding: 30px 15px;
            line-height: 0;
            position: sticky;
            top: 0;
            background-color: {colors.chart_background_color};
            z-index: 10;
        }}

        .styled-table tbody tr {{
            background-color: {colors.chart_background_color};
            border-bottom: 0px solid {colors.secondary_text_color};
            height: 5px;
            transition: background-color 0.3s ease;
        }}

        .styled-table tbody tr:hover {{
            background-color: {colors.secondary_chart_color};
            color: {colors.primary_text_color};
            cursor: pointer;
        }}

        .styled-table td {{
            border: none;
            padding: 20px 15px;
            vertical-align: middle;
        }}

        /* Alignment fixes */
        .styled-table td:nth-child(1),  /* Module_Type */
        .styled-table td:nth-child(2) {{ /* Completion_Rate */
            text-align: center;
        }}

        .styled-table td:nth-child(3) {{ /* Completion_Status */
            text-align: left;
        }}

        .grade-chip {{
            display: inline-block;
            color: white;
            width: 70px;
            height: 30px;
            line-height: 30px;
            text-align: center;
            padding: 4px 12px;
            border-radius: {border_radius_px}px;
            font-size: {subtitle_font_size_rem}rem;
            white-space: nowrap;
        }}
    </style>
    {html}
    """

    # Render in Streamlit
    components.html(html_string, height=600, width=5000, scrolling=True)

#######################
# Helper Functions for Utility

def recommend_modules(main_major, k=3):

    data = electives_ranking.copy()

    min_score = data['popularity_score'].min()
    max_score = data['popularity_score'].max()
    if min_score == max_score:
        data['rank'] = pd.Series([5] * len(data['popularity_score']))
    else:
        data['rank'] = 1 + 9 * (data['popularity_score']) / (max_score - min_score)
    
    data = data[['Module_Code', 
                 'Module_Type',
                'Module_Title', 
                'DVR_scaled', 
                'Oversubscribed_weighted_scaled',
                'LR_Coefficient_scaled',
                'CoV_scaled',
                'popularity_score',
                'rank']]

    if main_major is not None:
        
        data = data[data['Module_Type']==main_major].sort_values(by='rank', ascending=False)
        data = data.head(k)
        return set(data['Module_Code']), data
    else:
        data = data.sort_values(by='rank', ascending=False)
        data = data.head(k)
        return set(data['Module_Code']), data

#######################
# Reading Sample Data

sample_data = load_excel_file_bytes('./data/sample_data.xlsx')

# -------------------------
# Page 1: Download Sample File
# -------------------------

if 'page' not in st.session_state:
    st.session_state.page = 'download'

if st.session_state.page == 'download':

    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        for _ in range(10):
            render_space()

        # -- NUS Logo:

        img_base64 = get_base64_image("./images/NUS_Logo.png")
        st.markdown(
            f"""
            <div style="text-align: center;">
                <img src="data:image/png;base64,{img_base64}" alt="NUS Logo" width="500">
            </div>
            """,
            unsafe_allow_html=True
        )

        # -- Style Download Page (Header, Subtext, Download button, Page Transition button):

        style_download_page(main_text="Step 1: 📥 Download!",
                            sub_text="Don't have an excel template? Downwload one below",
                            maintext_color="#1b46f2",
                            maintext_fontsize=f"{title_font_size_px * 2}px",
                            subtext_color="#000000",
                            subtext_fontsize=f"{title_font_size_px}px",
                            download_button_bgcolor="#fa4202",
                            download_button_textcolor="#ffffff",
                            download_button_hovercolor="#fa4202",
                            page_transition_bgcolor="#fa4202",
                            page_transition_textcolor="#ffffff",
                            page_transition_hovercolor="#fa4202")
                            
        # -- Download button:

        st.download_button(
            label="Download Sample File",
            data=sample_data,
            file_name="sample_grades.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download-sample"
        )

        # -- Page transition (Go to Upload) button:

        st.markdown('<div class="big-button">', unsafe_allow_html=True)
        if st.button("Go to Upload", key="next-btn"):
            st.session_state.page = 'upload'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# Page 2: Upload File
# -------------------------
elif st.session_state.page == 'upload':

    col1, col2, col3 = st.columns([1,1,1])

    with col2:

        for _ in range(10):
            render_space()
        
        # -- Style Upload Page (Header, Uploader, Page Transition button):

        style_upload_page(main_text="Step 2: 📤 Upload!",
                          maintext_color="#1b46f2",
                          maintext_fontsize=f"{title_font_size_px * 2}px",
                          uploader_bgcolor="#fa4202",
                          uploader_fontcolor="#ffffff",
                          uploader_fontsize=f"{title_font_size_px}px",
                          page_transition_bgcolor="#fa4202",
                          page_transition_textcolor="#ffffff",
                          page_transition_hovercolor="#fa4202")

        # -- Upload Excel File:

        uploaded_file = st.file_uploader("", type=["xlsx"])
        if uploaded_file:
            df = load_uploaded_data(uploaded_file)
            if df is not None:
                st.session_state.uploaded_df = df
                if st.button("Continue to Dashboard"):
                    st.session_state.page = 'dashboard'
                    st.rerun()
        else:
            st.info("Please upload the completed Excel file.")
        
        # -- Page transition (Back) button:

        if st.button("Back to Download"):
            st.session_state.page = 'download'
            st.rerun()

# -------------------------
# Page 3: Dashboard
# -------------------------
elif st.session_state.page == 'dashboard':

    # -- Reinstate main data source:

    df = st.session_state.uploaded_df

    #######################
    # Side Bar

    with st.sidebar:

        # -- Color Theme Widget:

        theme_options = ["Light", "Dark"]
        theme = st.selectbox("Select a Color Theme:", options=theme_options)

        # -- Initialize Color Palette:

        colors = ColorPalette(theme)

        # -- Style Color Theme Widget based on Color Theme:

        style_widget_label(label="Select a Color Theme:",
                           color=colors.primary_text_color,
                           font_size='40px',
                           font_weight='300')

        # -- Track & Major Multiselect Widget:

        selected_tracks = st.multiselect(
            "Filter Your Track & Major:",
            options=df['Module_Type'].unique(),
            default=df['Module_Type'].unique(),
        )

        # -- Style Track & Major Multiselect Widget based on Color Theme:
        
        style_widget_label(label="Filter Your Track & Major:",
                           color=colors.primary_text_color,
                           font_size='40px',
                           font_weight='300')
        
        # -- Main Major Selection Widget:

        specialisation_options = [track for track in selected_tracks if (
            track.startswith('BBA-') and
            track not in ["BBA-BE", "BBA-BF", "BBA-FSP"]
        )]

        main_major = st.selectbox("Select Your Main Major:", options=specialisation_options)

        # -- Style Main Major Selection Widget based on Color Theme:
        
        style_widget_label(label="Select Your Main Major:",
                           color=colors.primary_text_color,
                           font_size='40px',
                           font_weight='300')
        
        # -- Additional Data Preprocessing:

        df['GPA'] = df['Grade'].map(grade_point_mapper)
        df['Term'] = (df['Year'].astype(str) + df['Semester'].astype(str)).astype(int)
        df['Module_Type_UE'] = df['Module_Type'].apply(
                                    lambda x : (
                                        x if x in ['BBA-BE', 'BBA-BF', 'BBA-FSP', 'GE', 'UE', main_major] else
                                        'UE' if x.startswith('MINOR-') else
                                        'UE' if x.startswith('MAJOR-') else
                                        'UE'
                                    )
                                )

        # -- Initialize User:

        if "user" not in st.session_state:
            st.session_state.user = User(raw_data=df)
        user = st.session_state.user

         # -- Apply Filtering:

        user.main_major = main_major
        user.apply_filter(selected_tracks)

        if user.filtered_data is None or user.filtered_data.empty:
            st.markdown(
                f"""
                <div style="
                    background-color: {colors.primary_chart_color};
                    color: white;
                    padding:16px;
                    border-left:6px solid {colors.secondary_chart_color};
                    border-radius:8px;
                    font-weight:500;">
                    ⚠️ No data available based on the current filter settings!
                </div>
                """,
                unsafe_allow_html=True
            )
            st.stop()
            
        # -- Page Transition (Back to Upload) button:

        style_page_transition_button(bgcolor=colors.app_bgcolor, 
                                     textcolor=colors.secondary_text_color, 
                                     hovercolor=colors.primary_text_color)
        
        if st.button("Back to Upload"):
            st.session_state.page = 'upload'
            st.rerun()

        # -- Style App:

        style_app_background(bgcolor=colors.app_bgcolor,
                             clickcolor=colors.primary_text_color)
        
        style_sidebar(bgcolor=colors.chart_background_color,
                      widget_bgcolor=colors.app_bgcolor,
                      multiselect_tagcolor=colors.chart_background_color,
                      textcolor=colors.primary_text_color)
        
        round_plotly_corners()

    #######################
    # Dashboard

    completion_rate = user.snapshot.completion_rate
    completion_rate = min(completion_rate, 100)

    main_col1, main_col2 = st.columns([0.2, 0.7], gap='medium')

    with main_col1:
        
        # -- CGPA Box, Metric Boxes, Degree Completion Donut:

        total_MCs_dark_icon = get_base64_image("./images/total_MCs.png")
        cgpa_dark_icon = get_base64_image("./images/cgpa.png")
        SU_dark_icon = get_base64_image("./images/SU.png")
        study_year_dark_icon = get_base64_image("./images/study_year.png")

        total_MCs_light_icon = get_base64_image("./images/total_MCs_light.png")
        cgpa_light_icon = get_base64_image("./images/cgpa_light.png")
        SU_light_icon = get_base64_image("./images/SU_light.png")
        study_year_light_icon = get_base64_image("./images/study_year_light.png")

        if theme == 'Dark':
            total_MCs_icon = total_MCs_dark_icon
            cgpa_icon = cgpa_dark_icon
            SU_icon = SU_dark_icon
            study_year_icon = study_year_dark_icon
        else:
            total_MCs_icon = total_MCs_light_icon
            cgpa_icon = cgpa_light_icon
            SU_icon = SU_light_icon
            study_year_icon = study_year_light_icon

        render_CGPA_box(label="Cumulative GPA", sublabel="Out of 5.0",value=user.snapshot.cgpa)
        render_space()

        render_metric_box(label='Total MCs', 
                          sublabel='Out of 160', 
                          value=user.snapshot.total_units, 
                          icon=total_MCs_icon,
                          bg_color=colors.chart_background_color,
                          text_color=colors.primary_text_color,
                          subtext_color=colors.secondary_text_color) 
        render_space()
        
        render_metric_box(label='Remaining S/Us', 
                          sublabel='Out of 32', 
                          value= user.snapshot.SU_used, 
                          icon=SU_icon,
                          bg_color=colors.chart_background_color,
                          text_color=colors.primary_text_color,
                          subtext_color=colors.secondary_text_color) 
        render_space()

        render_metric_box(label='Year of Study', 
                          sublabel='Out of 4', 
                          value= user.snapshot.current_year, 
                          icon=study_year_icon,
                          bg_color=colors.chart_background_color,
                          text_color=colors.primary_text_color,
                          subtext_color=colors.secondary_text_color) 
        render_space()

        render_degree_completion_donut(completion_rate=completion_rate)

    with main_col2:

        sub_col1, sub_col2 = st.columns([0.4, 0.6], gap='medium')
        
        with sub_col1:

            # -- CGPA Line Chart, CGPA Bar Chart, Track Progress Multilayered Donut:

            render_cgpa_trend_waterfallchart(df=user.filtered_data)
            
            render_space()
            
            track_gpas = normalize_completion_status(user.snapshot.track_status)
            track_gpas['CGPA'].fillna(0, inplace=True)
            render_track_gpa_barchart(track_gpas)
            
            render_space()

            track_status = normalize_completion_status(user.snapshot.track_status)
            render_track_progress_donut(track_status)
        
        with sub_col2:

            # -- Recommended Modules, Track Progress Table:

            top_modules, top_modules_df = recommend_modules(main_major=user.main_major)
            render_demand_vacancy_trends(elective_df=top_modules_df, 
                                         demand_df=bba_electives_demand_vacancy_data,
                                         top_modules=top_modules); render_space()
            
            render_table(track_status)

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

