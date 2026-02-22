import streamlit as st
import requests
import random, math, pandas as pd

URL = "https://lite.playbetman.com/league/P6FAI/..."

st.set_page_config(page_title="PlayBetMan Predictor", layout="wide")
st.title("PlayBetMan Predictor (Monte Carlo + Bayesian + Exponential Weighting)")

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

if st.button("Run Predictions"):
    response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    text_blocks = response.text.splitlines()  # flatten into lines
    fixtures = []

    for i in range(len(text_blocks)):
        if text_blocks[i].strip() == "1":  # odds start marker
            try:
                home_odds = text_blocks[i+1].strip()
                draw_odds = text_blocks[i+3].strip() if text_blocks[i+2].strip() == "X" else None
                away_odds = text_blocks[i+5].strip() if text_blocks[i+4].strip() == "2" else None

                home = text_blocks[i-3].strip()
                away = text_blocks[i-1].strip()

                if home_odds and draw_odds and away_odds:
                    fixtures.append((home, away, home_odds, draw_odds, away_odds))
            except Exception:
                continue

    if not fixtures:
        st.warning("⚠️ No odds found — check site structure.")
    else:
        for i, (home, away, home_odds, draw_odds, away_odds) in enumerate(fixtures, start=1):
            try:
                float(home_odds); float(draw_odds); float(away_odds)
            except ValueError:
                st.write(f"Match {i}: {home} vs {away} → Odds invalid, skipping.")
                continue

            st.subheader(f"Match {i}: {home} vs {away}")
            st.write(f"Odds → Home: {home_odds}, Draw: {draw_odds}, Away: {away_odds}")

            prediction, confidence, dist = monte_carlo_simulation(home, away, home_odds, draw_odds, away_odds)
            st.info(f"🔮 Predicted Outcome: {prediction} ({confidence*100:.2f}% confidence)")

            df = pd.DataFrame({"Outcome": list(dist.keys()), "Probability": list(dist.values())})
            st.bar_chart(df.set_index("Outcome"))
