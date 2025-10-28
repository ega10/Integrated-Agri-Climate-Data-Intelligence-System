Integrated Agri-Climate Data Intelligence System
Overview

This project integrates agricultural production data from https://data.gov.in
 with climate (rainfall) data to build an intelligent system that can answer natural-language questions about crop production, rainfall, and agricultural policy insights.

It demonstrates a complete data pipeline — from data acquisition and integration to AI-assisted question answering — for agriculture-based data analysis.

Features

Automatic Data Fetching (Phase 1)

Fetches live crop production data via the official data.gov.in API (only once).

Cleans and merges it with offline rainfall data.

Stores the integrated dataset locally for reuse.

Natural-Language Query Interface (Phase 2)

Understands simple English questions such as:

Compare rainfall in Tamil Nadu and Kerala

Top 5 crops in Punjab

Trend of rice in Maharashtra

Recommend paddy vs millet in Rajasthan

Rainfall in Tamil Nadu in 2020

Automatically detects state, crop, and year names using fuzzy text matching.

Answers with relevant statistics and insights.

System Architecture

Data Acquisition Layer
Uses the Data.gov.in API for agricultural production data and loads local rainfall dataset (climate.csv).

Data Processing Layer
Cleans, normalizes, and merges datasets. Saves the integrated file (integrated_dataset.csv) for fast access.

Query Engine
Processes user questions in simple English. Extracts intent such as compare, top crops, trend, policy, or rainfall. Uses pandas-based analysis to generate answers.

Output Layer
Displays readable summaries of production and rainfall insights.

Folder Structure
project/
│
├── data/
│   ├── climate.csv                # Offline rainfall dataset
│   └── integrated_dataset.csv     # Auto-generated merged dataset
│
├── .env                           # Contains your API key
├── integrated.py                  # Main Python script
├── README.md                      # Project documentation
└── requirements.txt               # Python dependencies

Setup Instructions
Step 1: Clone the Repository
git clone https://github.com/your-username/agri-climate-intelligence.git
cd agri-climate-intelligence

Step 2: Install Dependencies
pip install -r requirements.txt

Step 3: Add API Key

Create a .env file in the project folder and add:

API_KEY=your_datagovin_api_key_here


You can obtain your API key by creating a free account at https://data.gov.in
.

Step 4: Add Rainfall Data

Place your climate.csv file in the /data folder.
The file should contain columns:

SUBDIVISION, YEAR, ANNUAL

Running the Project
First Run (Data Fetching)
python phase2_agri_system.py


The system fetches agricultural data using your API key, merges it with rainfall data, and creates integrated_dataset.csv.
Once saved, future runs will load the local dataset without fetching again.

Second Run (Query Mode)

After the data is stored, run the script again to ask questions:

python phase2_agri_system.py


Example queries:

Ask: compare rainfall in Tamil Nadu and Kerala
Ask: top 3 crops in Punjab
Ask: trend of rice in Maharashtra
Ask: recommend paddy vs millet in Rajasthan
Ask: rainfall in Tamil Nadu in 2020


To exit:

Ask: exit

Example Output

Question:

compare rainfall in Tamil Nadu and Kerala


Output:

Average rainfall (last 5 years):
State
Kerala        2890.54
Tamil Nadu     875.32


Question:

recommend paddy vs millet in Rajasthan


Output:

Policy Insight for Rajasthan:
- Paddy: Avg production = 180.43 tonnes, Avg rainfall = 512.60 mm
- Millet: Avg production = 275.90 tonnes, Avg rainfall = 410.25 mm

Key Design Choices

Data is fetched only once and cached for faster future use.

Fuzzy text matching allows flexible queries such as “Tamilnadu” or “Kerela”.

Accepts plain English input without requiring structured syntax.

Scalable and easy to extend for district-level or weather-based questions.

Future Enhancements

Add district-level and crop-type filters.

Include real-time weather APIs for live rainfall data.

Create a simple front-end chatbot using React or Streamlit.

Use an NLP model like spaCy or transformers for advanced language understanding.

Author and Credits

Developer: Egadarshan S
Data Sources:

data.gov.in Agriculture API

IMD Rainfall Statistics (offline CSV)
