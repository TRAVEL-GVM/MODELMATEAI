# ModelMateAI

**ModelMateAI** is a **Streamlit** tool used to analyse and interact with recorded **Findings**, **Obligations**, and **Recommendations** related to Internal Risk Models under Models Committee management.

Its primary goal is to centralize and analyse recorded activities that would otherwise not be captured by Internal Control's WFMII system — such as findings related to models not yet in production or recommendations that wouldn’t be registered on time (e.g., regarding draft ECB decisions).

An integration with **Large Language Models (LLMs)** was implemented to allow natural language interaction with the findings, enabling easier access, deeper understanding, and visual exploration of the data.

---

## 🧠 Key Features

- ✅ **Data Quality Checks**  
  Automatically detects missing values, formatting issues, and data inconsistencies.

- 📊 **Exploratory Data Analysis**  
  Summary statistics, visual insights, and charting of findings.

- 💬 **Natural Language Querying**  
  Ask questions about the database using plain English. Powered by LLMs.

- 📈 **Interactive Visualizations**  
  Generate plots and explore trends over time directly through the app.

---

## 📁 Project Structure

MODELMATEAI/
│
├── ModelM/
│ └── data/ # CSV files exported from SharePoint ModelMate list
│
├── data/
│ ├── app.py # Streamlit frontend logic
│ ├── config.py # Configurations and constants
│ ├── functions.py # Helper functions for querying and display
│ ├── get_data.py # Loads and preprocesses data from the CSVs
│ ├── prompts.py # Prompt templates for LLM interactions
│ ├── pandasai.log # Log from pandasai (LLM backend)
│ └── requirements.txt # Python dependencies
│
├── .gitignore
└── README.md


> ℹ️ **Note**: The data used by this app is exported from the SharePoint list associated with the ModelMate internal platform. The CSV files are placed under the `ModelM/data/` folder.

---

## ⚙️ How to Run the App Locally

1. **Clone the repository**

```bash
git clone https://github.com/TRAVEL-GVM/MODELMATEAI.git
cd MODELMATEAI

2. **(Optional)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
