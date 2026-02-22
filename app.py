import streamlit as st
import requests
import re
import random
import math
import pandas as pd

URL = "https://lite.playbetman.com/league/P6FAI/..."

st.set_page_config(page_title="PlayBetMan Predictor", layout="wide")
st.title("PlayBetMan Predictor (Monte Carlo + Bayesian + Exponential Weighting + Trend Tracker)")

def advanced_probabilities(home_odds, draw_odds, away_odds, alpha=0.5, beta=0.05):
    weights = [
        math.exp(-alpha * float(home_odds)),
        math.exp(-alpha * float(draw_odds)),
        math.exp(-alpha * float(away_odds))
    ]
    total = sum(weights)
    weights = [w/total for w in weights]
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

def trend_arrow(new, old):
    try:
        new, old = float(new), float(old)
        if new < old: return "↓"
        elif new > old: return "↑"
        else: return "→"
    except:
        return "?"

if st.button("Run Predictions"):
    response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    html = response.text

    fixtures = re.findall(
        r"MPLY-[^\n]+\n([^\n]+)\nMPLY-[^\n]+\n([^\n]+)\n1\n([\d.]+)\nX\n([\d.]+)\n2\n([\d.]+)",
        html
    )

    if not fixtures:
        st.warning("⚠️ No odds found in page structure.")
    else:
        if "previous_odds" not in st.session_state:
            st.session_state.previous_odds = {}

        for i, (home, away, home_odds, draw_odds, away_odds) in enumerate(fixtures, start=1):
            match_key = f"{home} vs {away}"
            prev = st.session_state.previous_odds.get(match_key, (home_odds, draw_odds, away_odds))

            st.subheader(f"Match {i}: {home} vs {away}")
            st.write(
                f"Odds → Home: {home_odds} {trend_arrow(home_odds, prev[0])}, "
                f"Draw: {draw_odds} {trend_arrow(draw_odds, prev[1])}, "
                f"Away: {away_odds} {trend_arrow(away_odds, prev[2])}"
            )

            prediction, confidence, dist = monte_carlo_simulation(home, away, home_odds, draw_odds, away_odds)
            st.info(f"🔮 Predicted Outcome: {prediction} ({confidence*100:.2f}% confidence)")

            df = pd.DataFrame({
                "Outcome": list(dist.keys()),
                "Probability": list(dist.values())
            })
            st.bar_chart(df.set_index("Outcome"))

            # Save current odds for trend tracking
            st.session_state.previous_odds[match_key] = (home_odds, draw_odds, away_odds)
