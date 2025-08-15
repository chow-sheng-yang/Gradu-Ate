import streamlit as st
import streamlit.components.v1 as components
from utils import *


'''
    1) This script initializes the color themes and styling methods for the app;
    2) This script is imported as a module.
'''

#######################
# ColorPalette class to control color themes

class ColorPalette:

    def __init__(self, color_theme='Light'):
        self.primary_chart_color = "#1b46f2"
        self.secondary_chart_color = "#fa4202"
        self.secondary_text_color = "#777777"

        if color_theme == 'Dark':
            self.app_bgcolor = "#141518"
            self.primaryColor = "#fa4202"
            self.secondaryColor = "#1f2125"
            self.chart_background_color = "#1f2125"
            self.primary_text_color = "#ffffff"

        elif color_theme == 'Light':
            self.app_bgcolor = "#f4f4f4"
            self.primaryColor = "#fa4202"
            self.secondaryColor = "#ffffff"
            self.chart_background_color = "#ffffff"
            self.primary_text_color = "#000000"

#######################
# Helper Functions for Styling Download Page

# -- Style Download Page elements:

def style_download_page(main_text,
                        sub_text,
                        maintext_color,
                        maintext_fontsize,
                        subtext_color,
                        subtext_fontsize,
                        download_button_bgcolor,
                        download_button_textcolor,
                        download_button_hovercolor,
                        page_transition_bgcolor,
                        page_transition_textcolor,
                        page_transition_hovercolor
                        ):
    st.markdown(f"""
        <style>
        .download-header {{
            text-align: center;
            font-size: {maintext_fontsize};
            color: {maintext_color};  /* Blue */
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}

        .download-subtext {{
            text-align: center;
            font-size: {subtext_fontsize};
            color: {subtext_color};
            margin-bottom: 2rem;
        }}
    </style>
    """, unsafe_allow_html=True)
    
    # Render header and subtext
    st.markdown(f"<div class='download-header'>{main_text}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='download-subtext'>{sub_text}</div>", unsafe_allow_html=True)

    style_download_data_button(bgcolor=download_button_bgcolor,
                               textcolor=download_button_textcolor,
                               hovercolor=download_button_hovercolor)
    
    style_page_transition_button(bgcolor=page_transition_bgcolor,
                                 textcolor=page_transition_textcolor,
                                 hovercolor=page_transition_hovercolor)

# -- Style Download Data button:

def style_download_data_button(bgcolor, textcolor, hovercolor):
    # Inject custom CSS to style the button
    st.markdown(f"""
        <style>
        div[data-testid="stDownloadButton"] {{
            display: flex;
            justify-content: center;
        }}

        div[data-testid="stDownloadButton"] > button {{
            background-color: {bgcolor} !important;
            color: {textcolor} !important;
            font-size: 16px !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            padding: 10px 24px !important;
            border: none !important;
            cursor: pointer;
        }}

        div[data-testid="stDownloadButton"] > button:hover {{
            background-color: {hovercolor} !important;
        }}
        </style>
    """, unsafe_allow_html=True)
    
#######################
# Helper Functions for Styling Upload Page

# -- Style Upload Page elements:

def style_upload_page(main_text,
                      maintext_color,
                      maintext_fontsize,
                      uploader_bgcolor,
                      uploader_fontcolor,
                      uploader_fontsize,
                      page_transition_bgcolor,
                      page_transition_textcolor,
                      page_transition_hovercolor):
    st.markdown(f"""
        <style>
            /* Centered header */
            .upload-header {{
                text-align: center;
                font-size: {maintext_fontsize};
                color: {maintext_color};  /* Blue */
                font-weight: 700;
                margin-bottom: 2rem;
            }}

            /* Style the file uploader background and text */
            section[data-testid="stFileUploader"] > div {{
                background-color: {uploader_bgcolor} !important;  /* Orange */
                color: {uploader_fontcolor} !important;
                border-radius: 10px;
                padding: 1rem;
                font-weight: bold;
                font-size: {uploader_fontsize};
            }}
        </style>
    """, unsafe_allow_html=True)

    # Coloring uploader
    st.markdown(f"""
        <style>
        /* Info box (change st.info background) */
        .stAlert {{
            background-color: #f1f3f5 !important;
            color: #373945 !important;
            border-radius: 8px;
            font-weight: 500;
        }}
         /* Target the text inside the st.info box */
        .stAlert > div {{
            color: #373945 !important;
        }}

        .stAlert p {{
            color: #373945 !important;
        }}
        </style>
        """, unsafe_allow_html=True)

    # Header
    st.markdown(f"<div class='upload-header'>{main_text}</div>", unsafe_allow_html=True)

    style_page_transition_button(bgcolor=page_transition_bgcolor,
                                 textcolor=page_transition_textcolor,
                                 hovercolor=page_transition_hovercolor)

#######################
# Helper Functions for Styling Dashboard

# -- Round border corners for Plotly charts:

def round_plotly_corners():
     st.markdown("""
        <style>
        div[data-testid="stPlotlyChart"] > div {
            border-radius: 60px !important;
            overflow: hidden !important;
            background-color: #0A1F44 !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        </style>
    """, unsafe_allow_html=True)

# -- Styles Dashboard Background:

def style_app_background(bgcolor, clickcolor):# Inject background color using CSS
    st.markdown(
        f"""
        <style>
            .stApp {{
                background-color: {bgcolor};
                color: {clickcolor};
            }}
        </style>
        """,
        unsafe_allow_html=True
    )

# -- Styles Dashboard Sidebar:

def style_sidebar(bgcolor, widget_bgcolor, multiselect_tagcolor, textcolor):
        
        # -- Padding & Spacing:
        st.markdown("""
            <style>
            section[data-testid="stSidebar"] > div:first-child {
                display: flex;
                flex-direction: column;
                justify-content: center;
                height: 100vh;
            }
            </style>
            """, unsafe_allow_html=True)

        # -- Sidebar background & text color
        st.markdown(f"""
            <style>
            section[data-testid="stSidebar"] {{
                background-color: {bgcolor} !important;
            }}
            </style>
        """, unsafe_allow_html=True)

        # -- Coloring background of Dropdown-Select & MultiSelect widgets, and font color of Dropdown-Select widget
        st.markdown(f"""
            <style>
            div[data-baseweb="select"] > div {{
                background-color: {widget_bgcolor} !important;
                color: {textcolor} !important;
            }}
            </style>
        """, unsafe_allow_html=True)

        # -- Coloring Multi-Select tag boxes only:
        st.markdown(f"""
            <style>
            .stMultiSelect [data-baseweb="tag"] {{
                background-color: {multiselect_tagcolor} !important;
                color: {textcolor} !important;
            }}
            </style>
        """, unsafe_allow_html=True)

        # -- Lock Sidebar:
        st.markdown("""
            <style>
            /* Lock the sidebar width and visibility */
            section[data-testid="stSidebar"] {
                width: 330px !important;
                min-width: 330px !important;
                max-width: 330px !important;
                overflow: visible !important;
                display: block !important;
                visibility: visible !important;
            }

            /* Remove resizer */
            div[data-testid="stSidebarResizer"] {
                display: none !important;
            }

            /* Remove toggle button */
            button[title="Hide sidebar"] {
                display: none !important;
            }

            /* Keep header and menu visible to avoid layout bugs */
            header, #MainMenu {
                visibility: visible !important;
            }
            </style>
        """, unsafe_allow_html=True)

        # -- Override widget borders (default + on hover/focus)
        st.markdown(f"""
            <style>
            div[data-baseweb="select"] > div {{
                border: 1px solid {widget_bgcolor} !important;  /* Normal border */
                box-shadow: none !important;
            }}

            div[data-baseweb="select"] > div:hover,
            div[data-baseweb="select"] > div:focus-within {{
                border: 1px solid {widget_bgcolor} !important;  /* Hover/Focus border */
                box-shadow: none !important;
            }}
            </style>
        """, unsafe_allow_html=True)

        # -- Optional Wrapper for Sidebar Content (if needed)
        st.markdown('<div id="sidebar-content">', unsafe_allow_html=True)

#######################
# Other Helper Functions
    
# -- Styles Page Transition buttons:

def style_transition_buttons():
    st.markdown(f"""
        <style>
            .stButton > button[kind], .stDownloadButton > button[kind] {{
                padding: 24px 40px !important;
                border-radius: 40px !important;
            }}
        </style>
    """, unsafe_allow_html=True)


# -- Styles Widget Text Labels:

def style_widget_label(label, color, font_weight, font_size):
    components.html(f"""
    <script>
    const labels = window.parent.document.querySelectorAll('p, label, span, div');
    const target = Array.from(labels).find(e => e.innerText.trim() === '{label}');
    if (target) {{
        target.style.setProperty('font-size', '{font_size}', 'important');
        target.style.setProperty('font-weight', '{font_weight}', 'important');
        target.style.setProperty('color', '{color}', 'important');
    }}
    </script>
    """, height=0)

# -- Styles Page Transition buttons:

def style_page_transition_button(bgcolor, textcolor, hovercolor):

    st.markdown(f"""
        <style>
        /* Center the entire stButton div */
        div.stButton {{
            display: flex;
            justify-content: center;
        }}

        /* Style the actual button */
        div.stButton > button {{
            background-color: {bgcolor} !important;
            color: {textcolor} !important;
            border-radius: 15px !important;
            font-weight: bold !important;
            padding: 0.5rem 1.5rem !important;
            font-size: 16px !important;
            border: none !important;
            transition: background-color 0.3s ease;
            cursor: pointer;
        }}

        div.stButton > button:hover {{
            background-color: {hovercolor} !important;
        }}
        </style>
    """, unsafe_allow_html=True)

# -- Render vertical spacing:

def render_space():
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)


