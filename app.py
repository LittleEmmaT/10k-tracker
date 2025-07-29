import streamlit as st
from datetime import datetime
import json

# Set page config
st.set_page_config(
    page_title="🏃‍♂️ 10K Quest Tracker",
    page_icon="🏃‍♂️",
    layout="wide"
)

# Initialize session state for data persistence
if 'tracker_data' not in st.session_state:
    st.session_state.tracker_data = {
        "total_xp": 0,
        "current_week": 1,
        "completed_activities": {},
        "run_data": {},
        "extra_workouts": [],
        "unlocked_badges": [],
        "pace_adjustments": {}
    }

# Weekly plans
WEEKLY_PLANS = {
    1: {
        "title": "Getting Started!",
        "activities": [
            {"day": "Mon", "activity": "REST or gentle yoga (15 mins)", "xp": 10, "type": "rest"},
            {"day": "Tue", "activity": "Easy run 2.5K", "xp": 10, "type": "run", "distance": "2.5K", "pace": "7:30-8:00/km", "structure": "Easy conversational pace throughout"},
            {"day": "Wed", "activity": "Strength training (20 mins)", "xp": 15, "type": "strength", "focus": "Foundation", "exercises": "Bodyweight squats (3x12), Push-ups (3x8-12), Plank (3x30sec), Glute bridges (3x15), Calf raises (3x15)"},
            {"day": "Thu", "activity": "Easy run 3K with pickups", "xp": 15, "type": "run", "distance": "3K", "pace": "7:30/km easy + 6:30/km pickups", "structure": "Warm up 1K easy, then 3 x 30sec at 6:30/km with 90sec recovery"},
            {"day": "Fri", "activity": "REST or yoga (15 mins)", "xp": 10, "type": "rest"},
            {"day": "Sat", "activity": "Parkrun 5K", "xp": 25, "type": "run", "distance": "5K", "pace": "7:00/km target", "structure": "Race effort - aim for consistent pace"},
            {"day": "Sun", "activity": "Easy run 3.5K", "xp": 15, "type": "run", "distance": "3.5K", "pace": "7:30-8:00/km", "structure": "Relaxed long run pace"}
        ],
        "total_distance": "14K",
        "playlist": "Monday Motivation - Epic movie soundtracks"
    },
    2: {
        "title": "Building Confidence", 
        "activities": [
            {"day": "Mon", "activity": "Yoga/mobility (15 mins)", "xp": 10, "type": "yoga"},
            {"day": "Tue", "activity": "Easy run 3K", "xp": 10, "type": "run", "distance": "3K", "pace": "7:30-8:00/km", "structure": "Steady easy pace throughout"},
            {"day": "Wed", "activity": "Strength + core (25 mins)", "xp": 15, "type": "strength", "focus": "Building", "exercises": "Squats (3x15), Push-ups (3x10-15), Side plank (3x20sec each), Single-leg glute bridges (3x10 each)"},
            {"day": "Thu", "activity": "Fartlek 3K", "xp": 15, "type": "run", "distance": "3K", "pace": "7:30/km easy + 6:15/km fast", "structure": "800m warm up, then 4 x (1min fast, 2min easy), cool down"},
            {"day": "Fri", "activity": "REST", "xp": 0, "type": "rest"},
            {"day": "Sat", "activity": "Parkrun 5K", "xp": 25, "type": "run", "distance": "5K", "pace": "6:50-7:00/km", "structure": "Aim to be 10-15 seconds faster than last week"},
            {"day": "Sun", "activity": "Long run 4K", "xp": 20, "type": "run", "distance": "4K", "pace": "7:45-8:00/km", "structure": "Comfortable long run pace"}
        ],
        "total_distance": "15K",
        "playlist": "Tuesday Time Travel - Pick your decade!"
    }
}

def main():
    data = st.session_state.tracker_data
    
    # Header
    st.title("🏃‍♂️ 10K Quest Tracker")
    
    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total XP", data["total_xp"])
    with col2:
        st.metric("Current Week", f"{data['current_week']}/18")
    with col3:
        st.metric("Badges", len(data["unlocked_badges"]))
    
    # Week navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Previous", use_container_width=True) and data["current_week"] > 1:
            data["current_week"] -= 1
            st.rerun()
    with col3:
        if st.button("➡️ Next", use_container_width=True) and data["current_week"] < 18:
            data["current_week"] += 1
            st.rerun()
    
    # Current week plan
    current_plan = WEEKLY_PLANS.get(data["current_week"], WEEKLY_PLANS[1])
    
    st.header(f"Week {data['current_week']}: {current_plan['title']}")
    
    # Progress
    completed_count = sum(1 for activity in current_plan["activities"] 
                         if data["completed_activities"].get(f"week{data['current_week']}_{activity['day']}", False))
    progress = completed_count / len(current_plan["activities"])
    st.progress(progress, f"Progress: {completed_count}/{len(current_plan['activities'])} completed")
    
    # Playlist
    st.info(f"🎵 **This Week's Playlist:** {current_plan['playlist']}")
    
    # Activities
    st.subheader("This Week's Activities")
    
    for activity in current_plan["activities"]:
        key = f"week{data['current_week']}_{activity['day']}"
        is_completed = data["completed_activities"].get(key, False)
        
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                title = f"**{activity['day']}: {activity['activity']}**"
                st.markdown(title)
                
                if is_completed and key in data["run_data"]:
                    run_info = data["run_data"][key]
                    feeling_emoji = {"great": "🔥", "good": "😊", "okay": "😐", "tough": "😤", "bad": "😵"}
                    st.success(f"✅ {run_info['distance']} at {run_info['pace']} - Felt {feeling_emoji.get(run_info['feeling'], '😐')} {run_info['feeling']}")
                elif is_completed:
                    st.success("✅ Completed!")
            
            with col2:
                st.metric("XP", activity["xp"])
            
            # Buttons
            if activity["type"] in ["run"]:
                if not is_completed:
                    if st.button(f"🏃‍♂️ Log {activity['day']} Run", key=f"log_{key}", use_container_width=True):
                        st.session_state.logging_run = {
                            "activity": activity,
                            "key": key
                        }
                        st.rerun()
                else:
                    st.success("Run completed! ✅")
            else:
                if st.button(f"{'✅ Complete' if not is_completed else '✅ Completed'}", 
                           key=f"complete_{key}", use_container_width=True,
                           type="primary" if not is_completed else "secondary"):
                    data["completed_activities"][key] = not is_completed
                    if not is_completed:
                        data["total_xp"] += activity["xp"]
                    else:
                        data["total_xp"] -= activity["xp"]
                    st.rerun()
            
            # Activity details
            if activity["type"] == "run":
                with st.expander(f"🎯 Garmin Setup - {activity['day']}", expanded=False):
                    st.write(f"**Distance:** {activity['distance']}")
                    st.write(f"**Target Pace:** {activity['pace']}")
                    st.write(f"**Structure:** {activity['structure']}")
            elif activity["type"] == "strength":
                with st.expander(f"💪 Strength Focus - {activity['day']}", expanded=False):
                    st.write(f"**Focus:** {activity.get('focus', 'General')}")
                    st.write(f"**Exercises:** {activity.get('exercises', 'See plan')}")
            
            st.divider()
    
    # Run logging form
    if hasattr(st.session_state, 'logging_run'):
        st.markdown("---")
        st.subheader(f"🏃‍♂️ Log Your Run: {st.session_state.logging_run['activity']['activity']}")
        
        with st.form("run_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                distance = st.text_input("Distance Completed", placeholder="e.g. 2.5K")
                pace = st.text_input("Average Pace", placeholder="e.g. 7:30/km")
            
            with col2:
                feeling = st.selectbox("How did it feel?", [
                    "Select...",
                    "🔥 Great - Felt strong!",
                    "😊 Good - Right on target",
                    "😐 Okay - Got through it", 
                    "😤 Tough - Struggled a bit",
                    "😵 Bad - Really difficult"
                ])
            
            notes = st.text_area("Notes (optional)")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("📝 Log Run", use_container_width=True, type="primary"):
                    if distance and pace and feeling != "Select...":
                        feeling_short = feeling.split(" - ")[0].replace("🔥 ", "great").replace("😊 ", "good").replace("😐 ", "okay").replace("😤 ", "tough").replace("😵 ", "bad")
                        
                        run_entry = {
                            "distance": distance,
                            "pace": pace,
                            "feeling": feeling_short,
                            "notes": notes
                        }
                        
                        key = st.session_state.logging_run['key']
                        data["run_data"][key] = run_entry
                        data["completed_activities"][key] = True
                        data["total_xp"] += st.session_state.logging_run['activity']["xp"]
                        
                        # Auto-adjust future paces
                        if feeling_short == "great":
                            st.success("Great run! Future paces will be slightly faster! 🚀")
                        elif feeling_short in ["tough", "bad"]:
                            st.info("Taking it easier next time - that's smart training! 💪")
                        
                        delattr(st.session_state, 'logging_run')
                        st.success("Run logged successfully! 🎉")
                        st.rerun()
                    else:
                        st.error("Please fill in all required fields")
            
            with col2:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    delattr(st.session_state, 'logging_run')
                    st.rerun()
    
    # Weekly XP summary
    st.markdown("---")
    weekly_xp = sum(activity["xp"] for activity in current_plan["activities"] 
                   if data["completed_activities"].get(f"week{data['current_week']}_{activity['day']}", False))
    
    consistency_bonus = 50 if completed_count == len(current_plan["activities"]) else 0
    total_week_xp = weekly_xp + consistency_bonus
    
    st.metric("This Week's XP", total_week_xp)
    if consistency_bonus:
        st.balloons()
        st.success("🎉 Consistency Bonus: +50 XP!")
    
    # Badges
    st.subheader("🏆 Achievement Badges")
    badges = [
        {"name": "Fire Starter 🔥", "desc": "Complete first week", "unlocked": data["current_week"] == 1 and completed_count == len(current_plan["activities"])},
        {"name": "Consistency King 👑", "desc": "Complete a full week", "unlocked": completed_count == len(current_plan["activities"])},
        {"name": "Speed Demon ⚡", "desc": "Have a great feeling run", "unlocked": any("great" in str(run.get("feeling", "")) for run in data["run_data"].values())},
    ]
    
    for badge in badges:
        if badge["unlocked"] and badge["name"] not in data["unlocked_badges"]:
            data["unlocked_badges"].append(badge["name"])
    
    col1, col2 = st.columns(2)
    for i, badge in enumerate(badges):
        with col1 if i % 2 == 0 else col2:
            if badge["unlocked"]:
                st.success(f"**{badge['name']}**\n{badge['desc']}")
            else:
                st.info(f"{badge['name']}\n{badge['desc']}")
    
    # Footer
    st.markdown("---")
    if data["current_week"] < 18:
        st.success(f"🎯 **Next Target:** Week {data['current_week'] + 1}")
    else:
        st.success("🏁 **Race Week!** You've made it!")

if __name__ == "__main__":
    main()
