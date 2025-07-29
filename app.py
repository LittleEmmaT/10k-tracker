import streamlit as st
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="🏃‍♂️ 10K Quest Tracker",
    page_icon="🏃‍♂️",
    layout="wide"
)

# Initialize data
if 'data' not in st.session_state:
    st.session_state.data = {
        "total_xp": 0,
        "current_week": 1,
        "completed": {},
        "run_logs": {},
        "badges": []
    }

# Weekly plans
PLANS = {
    1: {
        "title": "Getting Started!",
        "activities": [
            {"day": "Mon", "name": "REST or gentle yoga (15 mins)", "xp": 10, "type": "other"},
            {"day": "Tue", "name": "Easy run 2.5K", "xp": 10, "type": "run", "distance": "2.5K", "pace": "7:30-8:00/km", "notes": "Easy conversational pace throughout"},
            {"day": "Wed", "name": "Strength training (20 mins)", "xp": 15, "type": "strength", "focus": "Foundation", "details": "Bodyweight squats (3x12), Push-ups (3x8-12), Plank (3x30sec), Glute bridges (3x15), Calf raises (3x15)"},
            {"day": "Thu", "name": "Easy run 3K with pickups", "xp": 15, "type": "run", "distance": "3K", "pace": "7:30/km easy + 6:30/km pickups", "notes": "Warm up 1K easy, then 3 x 30sec at 6:30/km with 90sec recovery"},
            {"day": "Fri", "name": "REST or yoga (15 mins)", "xp": 10, "type": "other"},
            {"day": "Sat", "name": "Parkrun 5K", "xp": 25, "type": "run", "distance": "5K", "pace": "7:00/km target", "notes": "Race effort - aim for consistent pace"},
            {"day": "Sun", "name": "Easy run 3.5K", "xp": 15, "type": "run", "distance": "3.5K", "pace": "7:30-8:00/km", "notes": "Relaxed long run pace"}
        ],
        "playlist": "Monday Motivation - Epic movie soundtracks"
    },
    2: {
        "title": "Building Confidence",
        "activities": [
            {"day": "Mon", "name": "Yoga/mobility (15 mins)", "xp": 10, "type": "other"},
            {"day": "Tue", "name": "Easy run 3K", "xp": 10, "type": "run", "distance": "3K", "pace": "7:30-8:00/km", "notes": "Steady easy pace throughout"},
            {"day": "Wed", "name": "Strength + core (25 mins)", "xp": 15, "type": "strength", "focus": "Building", "details": "Squats (3x15), Push-ups (3x10-15), Side plank (3x20sec each), Single-leg glute bridges (3x10 each)"},
            {"day": "Thu", "name": "Fartlek 3K", "xp": 15, "type": "run", "distance": "3K", "pace": "7:30/km easy + 6:15/km fast", "notes": "800m warm up, then 4 x (1min fast, 2min easy), cool down"},
            {"day": "Fri", "name": "REST", "xp": 0, "type": "other"},
            {"day": "Sat", "name": "Parkrun 5K", "xp": 25, "type": "run", "distance": "5K", "pace": "6:50-7:00/km", "notes": "Aim to be 10-15 seconds faster than last week"},
            {"day": "Sun", "name": "Long run 4K", "xp": 20, "type": "run", "distance": "4K", "pace": "7:45-8:00/km", "notes": "Comfortable long run pace"}
        ],
        "playlist": "Tuesday Time Travel - Pick your decade!"
    }
}

def main():
    st.title("🏃‍♂️ 10K Quest Tracker")
    
    data = st.session_state.data
    
    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total XP", data["total_xp"])
    with col2:
        st.metric("Week", f"{data['current_week']}/18")
    with col3:
        st.metric("Badges", len(data["badges"]))
    
    # Week navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Prev") and data["current_week"] > 1:
            data["current_week"] -= 1
            st.rerun()
    with col3:
        if st.button("Next ➡️") and data["current_week"] < 18:
            data["current_week"] += 1
            st.rerun()
    
    # Current week
    plan = PLANS.get(data["current_week"], PLANS[1])
    st.header(f"Week {data['current_week']}: {plan['title']}")
    
    # Progress
    completed_count = 0
    for activity in plan["activities"]:
        key = f"w{data['current_week']}_{activity['day']}"
        if data["completed"].get(key, False):
            completed_count += 1
    
    progress = completed_count / len(plan["activities"])
    st.progress(progress, f"Progress: {completed_count}/{len(plan['activities'])} done")
    
    st.info(f"🎵 **Playlist:** {plan['playlist']}")
    
    # Activities
    st.subheader("This Week's Activities")
    
    for activity in plan["activities"]:
        key = f"w{data['current_week']}_{activity['day']}"
        is_done = data["completed"].get(key, False)
        
        st.markdown(f"### {activity['day']}: {activity['name']}")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            st.metric("XP", activity["xp"])
        
        with col1:
            if is_done:
                if key in data["run_logs"]:
                    log = data["run_logs"][key]
                    feeling_emoji = {"great": "🔥", "good": "😊", "okay": "😐", "tough": "😤", "bad": "😵"}
                    st.success(f"✅ **Completed:** {log['distance']} at {log['pace']} - Felt {feeling_emoji.get(log['feeling'], '😐')} {log['feeling']}")
                else:
                    st.success("✅ **Completed!**")
            else:
                if activity["type"] == "run":
                    st.write("**Run Details:**")
                    st.write(f"• Distance: {activity['distance']}")
                    
                    # Show adjusted pace if applicable
                    pace_to_show = activity['pace']
                    if "pace_adjustments" in data and key in data.get("pace_adjustments", {}):
                        adjustment = data["pace_adjustments"][key]
                        if adjustment == "faster":
                            pace_to_show = f"{activity['pace']} ⚡ (15 sec/km faster - you're crushing it!)"
                        elif adjustment == "easier":
                            pace_to_show = f"{activity['pace']} 💙 (15 sec/km easier - smart recovery)"
                    
                    st.write(f"• Target Pace: {pace_to_show}")
                    st.write(f"• Structure: {activity['notes']}")
                elif activity["type"] == "strength":
                    st.write(f"**Focus: {activity['focus']}**")
                    st.write(f"• {activity['details']}")
        
        # Buttons
        if activity["type"] == "run" and not is_done:
            st.markdown("**Log this run:**")
            
            # Create unique keys for each input
            distance_key = f"dist_{key}"
            pace_key = f"pace_{key}"
            feeling_key = f"feel_{key}"
            notes_key = f"notes_{key}"
            
            col1, col2 = st.columns(2)
            with col1:
                distance = st.text_input("Distance completed:", key=distance_key, placeholder="e.g. 2.5K")
                pace = st.text_input("Average pace:", key=pace_key, placeholder="e.g. 7:30/km")
            with col2:
                feeling = st.selectbox("How did it feel?", 
                    ["Select...", "🔥 Great", "😊 Good", "😐 Okay", "😤 Tough", "😵 Bad"], 
                    key=feeling_key)
            
            notes = st.text_area("Notes (optional):", key=notes_key)
            
            if st.button(f"📝 Log {activity['day']} Run", key=f"log_btn_{key}"):
                if distance and pace and feeling != "Select...":
                    # Save the run
                    feeling_clean = feeling.split(" ")[1].lower() if " " in feeling else feeling.lower()
                    data["run_logs"][key] = {
                        "distance": distance,
                        "pace": pace, 
                        "feeling": feeling_clean,
                        "notes": notes
                    }
                    data["completed"][key] = True
                    data["total_xp"] += activity["xp"]
                    
                    # Smart pace adjustments based on how you felt!
                    if feeling_clean == "great":
                        st.success(f"🎉 {activity['day']} run logged! +{activity['xp']} XP")
                        st.info("🚀 **Smart Training:** Since you felt great, your next few runs will have slightly faster target paces to challenge you more!")
                        
                        # Store adjustment for future runs
                        if "pace_adjustments" not in data:
                            data["pace_adjustments"] = {}
                        
                        # Adjust next 3 running days
                        current_week = data["current_week"]
                        for week_offset in range(0, 2):  # Next 2 weeks
                            for day in ["Tue", "Thu", "Sat", "Sun"]:
                                future_key = f"w{current_week + week_offset}_{day}"
                                if future_key not in data["completed"]:
                                    data["pace_adjustments"][future_key] = "faster"
                    
                    elif feeling_clean in ["tough", "bad"]:
                        st.success(f"🎉 {activity['day']} run logged! +{activity['xp']} XP")
                        st.info("💙 **Smart Training:** You pushed through a tough one! Your next few runs will have easier target paces to help you recover and build back up.")
                        
                        # Store adjustment for future runs
                        if "pace_adjustments" not in data:
                            data["pace_adjustments"] = {}
                        
                        # Adjust next 2 running days to be easier
                        current_week = data["current_week"]
                        for week_offset in range(0, 2):
                            for day in ["Tue", "Thu", "Sun"]:
                                future_key = f"w{current_week + week_offset}_{day}"
                                if future_key not in data["completed"]:
                                    data["pace_adjustments"][future_key] = "easier"
                    
                    else:
                        st.success(f"🎉 {activity['day']} run logged! +{activity['xp']} XP")
                    
                    # Clear the form inputs
                    for input_key in [distance_key, pace_key, feeling_key, notes_key]:
                        if input_key in st.session_state:
                            del st.session_state[input_key]
                    
                    st.rerun()
                else:
                    st.error("Please fill in distance, pace, and feeling!")
        
        elif activity["type"] != "run":
            if st.button(f"{'✅ Mark Complete' if not is_done else '✅ Completed'}", 
                        key=f"btn_{key}", 
                        disabled=is_done):
                data["completed"][key] = True
                data["total_xp"] += activity["xp"]
                st.success(f"🎉 +{activity['xp']} XP!")
                st.rerun()
        
        st.divider()
    
    # Weekly summary
    st.subheader("📊 This Week")
    weekly_xp = sum(activity["xp"] for activity in plan["activities"] 
                   if data["completed"].get(f"w{data['current_week']}_{activity['day']}", False))
    
    if completed_count == len(plan["activities"]):
        weekly_xp += 50  # Consistency bonus
        st.balloons()
        st.success("🎉 **WEEK COMPLETE! +50 Consistency Bonus!**")
    
    st.metric("This Week's XP", weekly_xp)
    
    # Badges
    st.subheader("🏆 Badges")
    
    # Check for new badges
    if data["current_week"] == 1 and completed_count == len(plan["activities"]) and "Fire Starter 🔥" not in data["badges"]:
        data["badges"].append("Fire Starter 🔥")
        st.success("🎉 **NEW BADGE:** Fire Starter 🔥")
    
    if completed_count == len(plan["activities"]) and "Consistency King 👑" not in data["badges"]:
        data["badges"].append("Consistency King 👑")
        st.success("🎉 **NEW BADGE:** Consistency King 👑")
    
    # Check for great run badge
    great_runs = any("great" in str(log.get("feeling", "")) for log in data["run_logs"].values())
    if great_runs and "Speed Demon ⚡" not in data["badges"]:
        data["badges"].append("Speed Demon ⚡")
        st.success("🎉 **NEW BADGE:** Speed Demon ⚡")
    
    # Display badges
    if data["badges"]:
        for badge in data["badges"]:
            st.success(f"🏆 **{badge}**")
    else:
        st.info("Complete activities to earn badges!")
    
    # Footer
    st.markdown("---")
    st.success(f"🎯 **Goal:** Complete 10K on November 30th in under 60 minutes!")
    
    if data["current_week"] < 18:
        st.info(f"💪 **Next up:** Week {data['current_week'] + 1}")

if __name__ == "__main__":
    main()
