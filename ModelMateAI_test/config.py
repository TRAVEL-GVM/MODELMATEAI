import openai
import os

dashboard_main_title = 'ModelMate AI'

# nb default colors for plots and excel
default_color1 = '#179297'
default_color2 = '#BFCE28'

sidebar_indicators = ('Raw data', 'Test 1')

nmd_data_path = 'https://raw.githubusercontent.com/TRAVEL-GVM/MODELMATEAI/main/ModelMateAI_test/data/mmd.xlsx'
travel_logo_url = "https://raw.githubusercontent.com/ricardoandreom/Webscrape/refs/heads/main/travel_logo.webp"

openai.api_key = os.getenv("OPEN_AI_KEY")


