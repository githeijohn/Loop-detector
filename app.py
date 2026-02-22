import streamlit as st
import requests
from lxml import html
from collections import Counter

URL = "https://www.betika.com/en-ke/ligi-bigi"

seen_results = []
loops = []

st.title("Betika Ligi Bigi Loop Detector")

if st.button("Fetch Ligi Bigi Matches"):
    headers = {"User-Agent": "Mozilla/5.0"}  # helps avoid blocking
    response = requests.get(URL, headers=headers)
    tree = html.fromstring(response.text)

    # Adjust selectors if Betika changes layout
    matches = tree.xpath("//div[@class='match-card']")

    for i, match in enumerate(matches, start=1):
        home = match.xpath(".//div[@class='home']/text()")
        away = match.xpath(".//div[@class='away']/text()")
        goals_home = match.xpath(".//span[@class='home-score']/text()")
        goals_away = match.xpath(".//span[@class='away-score']/text()")

        if home and away and goals_home and goals_away:
            home = home[0].strip()
            away = away[0].strip()
            goals_home = int(goals_home[0].strip())
            goals_away = int(goals_away[0].strip())

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
