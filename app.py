import streamlit as st
import random, math, pandas as pd

st.set_page_config(page_title="PlayBetMan Predictor", layout="wide")
st.title("PlayBetMan Predictor (Paste Odds + Trend Tracker)")

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

# Text area for pasting odds
raw_text = st.text_area("Paste odds text here:", height=300)

if st.button("Run Predictions") and raw_text.strip():
    lines = raw_text.splitlines()
    fixtures = []

    for i in range(len(lines)):
        if lines[i].strip() == "1":
            try:
                home_odds = lines[i+1].strip()
                draw_odds = lines[i+3].strip()
                away_odds = lines[i+5].strip()
                home = lines[i-3].strip()
                away = lines[i-1].strip()
                fixtures.append((home, away, home_odds, draw_odds, away_odds))
            except Exception:
                continue

    if not fixtures:
        st.warning("⚠️ No odds found in pasted text.")
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

            df = pd.DataFrame({"Outcome": list(dist.keys()), "Probability": list(dist.values())})
            st.bar_chart(df.set_index("Outcome"))

            # Save current odds for trend tracking
            st.session_state.previous_odds[match_key] = (home_odds, draw_odds, away_odds)
