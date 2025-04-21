#import openai
import os
import streamlit as st

dashboard_main_title = 'ModelMate AI'

# nb default colors for plots and excel
default_color1 = '#179297'
default_color2 = '#BFCE28'

sidebar_indicators = ('Raw data', 'Test 1')
nmd_data_path = "https://raw.githubusercontent.com/TRAVEL-GVM/MODELMATEAI/main/ModelM/data/MODELMATE.csv"
nmd_old_path = "https://raw.githubusercontent.com/TRAVEL-GVM/MODELMATEAI/main/ModelM/data/MM_OLD.csv"
travel_logo_url = "https://raw.githubusercontent.com/ricardoandreom/Webscrape/refs/heads/main/travel_logo.webp"

#openai.api_key = os.getenv("OPEN_AI_KEY")
api_key = st.secrets["openai"]["api_key"]
#"llsk-proj-u2aW2nmTWgvRPLNzg6H3U0qZJGQW9wpSuV4K1L3ca5G5WyPMujI9MDBOYxbW-deY_EYGu_QP-wT3BlbkFJQZeam7ieHPEjl6efxPCQHuLVTv0uf3LRzedLAJ1Hqner6B5AWKuz6_7uPcPoRd2En9eEy-8RMA"
#st.secrets["openai"]["api_key"]

mmd_str = """
<h6>The objective of Modelmate is to track and monitor the  status of findings identified by the Detetor, assigned to the sponsor, according to the model and segment.</h6>
"""


