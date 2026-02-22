import streamlit as st
import requests
from bs4 import BeautifulSoup
from collections import Counter

URL = "https://www.betika.com/en-ke/ligi-bigi"

seen_results = []
loops = []

st.title("Betika Ligi Bigi Loop Detector")

if st.button("Fetch Ligi Bigi Matches"):
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")

    # Betika Ligi Bigi selectors (confirmed structure)
    matches = soup.find_all("div", class_="match-card")

    for i, match in enumerate(matches, start=1):
        home = match.find("div", class_="home").text.strip()
        away = match.find("div", class_="away").text.strip()
        goals_home = int(match.find("span", class_="home-score").text.strip())
        goals_away = int(match.find("span", class_="away-score").text.strip())

        result = (home, goals_home, goals_away, away)

        # Loop detection
        if result in seen_results:
            loops.append((i, home, goals_home, goals_away, away))
            st.error(f"LOOP DETECTED at match {i}: {home} {goals_home} - {goals_away} {away}")
        else:
            st.success(f"Match {i}: {home} {goals_home} - {goals_away} {away}")
            seen_results.append(result)

        # Weighted prediction
        if seen_results:
            freq = Counter(seen_results)
            total = sum(freq.values())
            choices, weights = zip(*[(res, count/total) for res, count in freq.items()])
            predicted = choices[0]  # most frequent result
            st.info(f"🔮 Predicted Next: {predicted[0]} {predicted[1]} - {predicted[2]} {predicted[3]}")

    # Summary
    st.subheader("Season Summary")
    if loops:
        st.write("Loops detected:")
        for loop in loops:
            st.write(f"Match {loop[0]}: {loop[1]} {loop[2]} - {loop[3]} {loop[4]}")
    else:
        st.write("No loops detected this season!")
