import streamlit as st
import requests
import re
import random
import math
import pandas as pd
from datetime import datetime

URL = "https://lite.playbetman.com/league/P6FAI/..."

st.set_page_config(page_title="PlayBetMan Predictor", layout="wide")
st.title("PlayBetMan Predictor (Monte Carlo + Bayesian + Exponential Weighting)")

def advanced_probabilities(home_odds, draw_odds, away_odds, alpha=0.5, beta=0.05):
    # Exponential weighting
    weights = [
        math.exp(-alpha * float(home_odds)),
        math.exp(-alpha * float(draw_odds)),
        math.exp(-alpha * float(away_odds))
    ]
    total = sum(weights)
    weights = [w/total for w in weights]

    # Bayesian adjustment
    adjusted = [w + beta for w in weights]
    total_adj = sum(adjusted)
    return [a/total_adj for a in adjusted]

def monte_carlo_simulation(home, away, home_odds, draw_odds, away_odds, trials=10000):
    probs = advanced_probabilities(home_odds, draw_odds, away_odds)
    labels = ["Home Win", "Draw", "Away Win"]

    outcomes = random.choices(labels, weights=probs, k=trials)
    prediction = max(set(outcomes), key=outcomes.count)
    confidence = outcomes.count(prediction) / len(outcomes)
    dist = {label: outcomes.count(label)/len(outcomes) for label in labels}

    return prediction, confidence, dist

if st.button("Run Predictions"):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)
    html = response.text

    # Regex to capture fixtures with time + odds
    fixtures = re.findall(
        r"(\d{2}:\d{2})\nMPLY-[A-Za-z0-9. ]+\n([A-Za-z. ]+)\n([A-Za-z. ]+)\n1\n([\d.]+)\nX\n([\d.]+)\n2\n([\d.]+)",
        html
    )

    now = datetime.now()

    if not fixtures:
        st.warning("⚠️ No fixtures found. Odds may not be posted yet.")
    else:
        for i, (time_str, home, away, home_odds, draw_odds, away_odds) in enumerate(fixtures, start=1):
            try:
                # Convert odds to float safely
                float(home_odds); float(draw_odds); float(away_odds)
            except ValueError:
                st.write(f"Match {i}: {home} vs {away} → Odds not valid, skipping prediction.")
                continue

            match_time = datetime.strptime(time_str, "%H:%M")
            minutes_to_start = (match_time - now).seconds // 60

            st.subheader(f"Match {i}: {home} vs {away} (Starts at {time_str}, in {minutes_to_start} min)")
            st.write(f"Odds → Home: {home_odds}, Draw: {draw_odds}, Away: {away_odds}")

            prediction, confidence, dist = monte_carlo_simulation(home, away, home_odds, draw_odds, away_odds)

            st.info(f"🔮 Predicted Outcome: {prediction} ({confidence*100:.2f}% confidence)")

            # Native Streamlit bar chart
            df = pd.DataFrame({
                "Outcome": list(dist.keys()),
                "Probability": list(dist.values())
            })
            st.bar_chart(df.set_index("Outcome"))
