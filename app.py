import streamlit as st
import requests
from html.parser import HTMLParser
from collections import Counter

URL = "https://www.betika.com/en-ke/ligi-bigi"

seen_results = []
loops = []

class MatchParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.matches = []
        self.current = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "div" and attrs.get("class") == "match-card":
            self.current = {}
        elif tag == "div" and attrs.get("class") == "home":
            self.current["home"] = ""
        elif tag == "div" and attrs.get("class") == "away":
            self.current["away"] = ""
        elif tag == "span" and attrs.get("class") == "home-score":
            self.current["home_score"] = ""
        elif tag == "span" and attrs.get("class") == "away-score":
            self.current["away_score"] = ""

    def handle_data(self, data):
        if "home" in self.current and self.current["home"] == "":
            self.current["home"] = data.strip()
        elif "away" in self.current and self.current["away"] == "":
            self.current["away"] = data.strip()
        elif "home_score" in self.current and self.current["home_score"] == "":
            self.current["home_score"] = data.strip()
        elif "away_score" in self.current and self.current["away_score"] == "":
            self.current["away_score"] = data.strip()

    def handle_endtag(self, tag):
        if tag == "div" and "home" in self.current and "away" in self.current:
            self.matches.append(self.current)
            self.current = {}

st.title("Betika Ligi Bigi Loop Detector")

if st.button("Fetch Ligi Bigi Matches"):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)

    parser = MatchParser()
    parser.feed(response.text)

    for i, match in enumerate(parser.matches, start=1):
        home = match.get("home", "")
        away = match.get("away", "")
        goals_home = int(match.get("home_score", "0"))
        goals_away = int(match.get("away_score", "0"))

        result = (home, goals_home, goals_away, away)

        if result in seen_results:
            loops.append((i, home, goals_home, goals_away, away))
            st.error(f"LOOP DETECTED at match {i}: {home} {goals_home} - {goals_away} {away}")
        else:
            st.success(f"Match {i}: {home} {goals_home} - {goals_away} {away}")
            seen_results.append(result)

        if seen_results:
            freq = Counter(seen_results)
            total = sum(freq.values())
            choices, weights = zip(*[(res, count/total) for res, count in freq.items()])
            predicted = choices[0]
            st.info(f"🔮 Predicted Next: {predicted[0]} {predicted[1]} - {predicted[2]} {predicted[3]}")

    st.subheader("Season Summary")
    if loops:
        st.write("Loops detected:")
        for loop in loops:
            st.write(f"Match {loop[0]}: {loop[1]} {loop[2]} - {loop[3]} {loop[4]}")
    else:
        st.write("No loops detected this season!")
