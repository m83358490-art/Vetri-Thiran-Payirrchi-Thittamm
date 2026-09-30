 PocketSmart AI

Smart budget & recommendation assistant built with Streamlit + Google Gemini.


Setup

python -m venv venv
venv\Scripts\activate        # Windows  (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
cp .env.example .env         # add your key from https://aistudio.google.com/apikey
streamlit run app.py

Structure


app.py – Streamlit UI (dashboard, add transaction, AI advisor, goal planner)

utils/budget.py – budget math, 50/30/20 rule

utils/gemini_client.py – Gemini calls (advice, recommendations, auto-categorize)

data/sample_expenses.csv – sample data