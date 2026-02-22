import streamlit as st
import random
import itertools
from collections import Counter

# 20 Premier League teams
teams = [
    "Arsenal", "Chelsea", "Liverpool", "Man City", "Man United", "Tottenham",
    "Everton", "Leeds", "Leicester", "West Ham", "Newcastle", "Southampton",
    "Crystal Palace", "Brighton", "Wolves", "Aston Villa", "Burnley",
    "Norwich", "Watford", "Brentford"
]

# Storage
seen_results = []
loops = []
match_count = 0

st.title("Premier League Loop Detector with Prediction")

if st.button("Simulate Full Season"):
    fixtures = []
    for teamA, teamB in itertools.combinations(teams, 2):
        fixtures.append((teamA, teamB))  # home
        fixtures.append((teamB, teamA))  # away

    random.shuffle(fixtures)
    weeks = [fixtures[i:i+10] for i in range(0, len(fixtures), 10)]

    for week_num, week in enumerate(weeks, start=1):
        st.subheader(f"--- Week {week_num} ---")
        for teamA, teamB in week:
            goalsA = random.randint(0, 6)
            goalsB = random.randint(0, 6 - goalsA)
            result = (teamA, goalsA, goalsB, teamB)
            match_count += 1

            # Loop detection
            if result in seen_results:
                loops.append((match_count, teamA, goalsA, goalsB, teamB))
                st.error(f"LOOP DETECTED at match {match_count}: {teamA} {goalsA} - {goalsB} {teamB}")
            else:
                st.success(f"Match {match_count}: {teamA} {goalsA} - {goalsB} {teamB}")
                seen_results.append(result)

            # Weighted prediction
            if seen_results:
                freq = Counter(seen_results)
                total = sum(freq.values())
                choices, weights = zip(*[(res, count/total) for res, count in freq.items()])
                predicted = random.choices(choices, weights=weights, k=1)[0]
                st.info(f"🔮 Predicted Next: {predicted[0]} {predicted[1]} - {predicted[2]} {predicted[3]}")

    # Summary
    st.subheader("Season Summary")
    if loops:
        st.write("Loops detected:")
        for loop in loops:
            st.write(f"Match {loop[0]}: {loop[1]} {loop[2]} - {loop[3]} {loop[4]}")
    else:
        st.write("No loops detected this season!")
