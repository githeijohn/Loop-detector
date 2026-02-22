import streamlit as st
import requests
import re
import random
import math
import matplotlib.pyplot as plt
from datetime import datetime

URL = "https://lite.playbetman.com/league/P6FAI/44454d4f36352a50364641492a4b45532a31303030302e302a3432326232653339373466333464393662666366383734633464646139353837?from=initPlay&lang=en&isDemo=1#"

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
    fixtures = re.findall(r"(\d{2}:\d{2})\nMPLY-[A-Za-z0-9. ]+\n([A-Za-z. ]+)\n([A-Za-z. ]+)\n1\n([\d.]+)\nX\n([\d.]+)\n2\n([\d.]+)", html)

    now = datetime.now()

    for i, (time_str, home, away, home_odds, draw_odds, away_odds) in enumerate(fixtures, start=1):
        match_time = datetime.strptime(time_str, "%H:%M")
        minutes_to_start = (match_time - now).seconds // 60

        st.subheader(f"Match {i}: {home} vs {away} (Starts at {time_str}, in {minutes_to_start} min)")
        st.write(f"Odds → Home: {home_odds}, Draw: {draw_odds}, Away: {away_odds}")

        prediction, confidence, dist = monte_carlo_simulation(home, away, home_odds, draw_odds, away_odds)

        st.info(f"🔮 Predicted Outcome: {prediction} ({confidence*100:.2f}% confidence)")

        # Bar chart visualization
        fig, ax = plt.subplots()
        ax.bar(dist.keys(), dist.values(), color=['green','gray','red'])
        ax.set_ylim(0,1)
        ax.set_ylabel("Probability")
        ax.set_title(f"Outcome Distribution for {home} vs {away}")
        for label, prob in dist.items():
            ax.text(label, prob+0.01, f"{prob*100:.1f}%", ha='center')
        st.pyplot(fig)

    st.write("⏳ Auto-refresh every 2 minutes keeps predictions aligned with PlayBetMan’s match cycle.")
    st.experimental_rerun()
