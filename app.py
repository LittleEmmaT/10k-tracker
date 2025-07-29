import streamlit as st
import json
import os
from datetime import datetime
import sqlite3

# Set page config
st.set_page_config(
    page_title="🏃‍♂️ 10K Quest Tracker",
    page_icon="🏃‍♂️",
    layout="wide"
)

# Database setup for cloud persistence
def init_db():
    conn = sqlite3.connect('tracker.db')
    c = conn.cursor()
    
    # Create tables if they don't exist
    c.execute('''CREATE TABLE IF NOT EXISTS user_data
                 (key TEXT PRIMARY KEY, value TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS activities
                 (id INTEGER PRIMARY KEY, week INTEGER, day TEXT, 
                  completed INTEGER, run_data TEXT, timestamp TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS extra_workouts
                 (id INTEGER PRIMARY KEY, week INTEGER, name TEXT, 
                  xp INTEGER, notes TEXT, timestamp TEXT)''')
    
    conn.commit()
    conn.close()

def load_data():
    init_db()
    conn = sqlite3.connect('tracker.db')
    c = conn.cursor()
    
    # Get user data
    c.execute("SELECT value FROM user_data WHERE key = 'main_data'")
    result = c.fetchone()
    
    if result:
        data = json.loads(result[0])
    else:
        data = {
            "total_xp": 0,
            "unlocked_badges": [],
            "pace_adjustments": {},
            "current_week": 1
        }
    
    # Get activities
    c.execute("SELECT * FROM activities")
    activities = c.fetchall()
    
    # Get extra workouts
    c.execute("SELECT * FROM extra_workouts")
    workouts = c.fetchall()
    
    conn.close()
    
    # Process data
    data["completed_activities"] = {}
    data["run_data"] = {}
    data["extra_workouts"] = []
    
    for activity in activities:
        key = f"week{activity[1]}_{activity[2]}"
        data["completed_activities"][key] = bool(activity[3])
        if activity[4]:
            data["run_data"][key] = json.loads(activity[4])
    
    for workout in workouts:
        data["extra_workouts"].append({
            "id": workout[0],
            "week": workout[1],
            "name": workout[2],
            "xp": workout[3],
            "notes": workout[4],
            "timestamp": workout[5]
        })
    
    return data

def save_data(data):
    init_db()
    conn = sqlite3.connect('tracker.db')
    c = conn.cursor()
    
    # Save main data
    main_data = {
        "total_xp": data["total_xp"],
        "unlocked_badges": data["unlocked_badges"],
        "pace_adjustments": data["pace_adjustments"],
        "current_week": data["current_week"]
    }
    
    c.execute("INSERT OR REPLACE INTO user_data (key, value) VALUES (?, ?)",
              ('main_data', json.dumps(main_data)))
    
    # Clear and save activities
    c.execute("DELETE FROM activities")
    for key, completed in data["completed_activities"].items():
        week, day = key.replace('week', '').split('_')
        run_data_json = json.dumps(data["run_data"].get(key)) if key in data["run_data"] else None
        c.execute("INSERT INTO activities (week, day, completed, run_data, timestamp) VALUES (?, ?, ?, ?, ?)",
                  (int(week), day, int(completed), run_data_json, datetime.now().isoformat()))
    
    # Clear and save extra workouts
    c.execute("DELETE FROM extra_workouts")
    for workout in data["extra_workouts"]:
        c.execute("INSERT INTO extra_workouts (week, name, xp, notes, timestamp) VALUES (?, ?, ?, ?, ?)",
                  (workout["week"], workout["name"], workout["xp"], workout["notes"], workout.get("timestamp", datetime.now().isoformat())))
    
    conn.commit()
    conn.close()

# Weekly training plans
WEEKLY_PLANS = {
    1: {
        "title": "Getting Started!",
        "activities": [
            {"day": "Mon", "activity": "REST or gentle yoga (15 mins)", "xp": 10, "type": "rest"},
            {"day": "Tue", "activity": "Easy run 2.5K", "xp": 10, "type": "run", "distance": "2.5K", "base_pace": "7:30-8:00/km", "structure": "Easy conversational pace throughout"},
            {"day": "Wed", "activity": "Strength training (20 mins)", "xp": 15, "type": "strength", "focus": "Foundation", "exercises": "Bodyweight squats (3x12), Push-ups/knee push-ups (3x8-12), Plank (3x30sec), Glute bridges (3x15), Calf raises (3x15)"},
            {"day": "Thu", "activity": "Easy run 3K with pickups", "xp": 15, "type": "run", "distance": "3K", "base_pace": "7:30/km easy + 6:30/km pickups", "structure": "Warm up 1K easy, then 3 x 30sec at 6:30/km with 90sec easy recovery, cool down"},
            {"day": "Fri", "activity": "REST or yoga (15 mins)", "xp": 10, "type": "rest"},
            {"day": "Sat", "activity": "Parkrun 5K", "xp": 25, "type": "run", "distance": "5K", "base_pace": "7:00/km target", "structure": "Race effort - aim for consistent pace"},
            {"day": "Sun", "activity": "Easy run 3.5K", "xp": 15, "type": "run", "distance": "3.5K", "base_pace": "7:30-8:00/km", "structure": "Relaxed long run pace - should feel easy"}
        ],
        "total_distance": "14K",
        "playlist": "Monday Motivation - Epic movie soundtracks"
    },
    2: {
        "title": "Building Confidence",
        "activities": [
            {"day": "Mon", "activity": "Yoga/mobility (15 mins)", "xp": 10, "type": "yoga"},
            {"day": "Tue", "activity": "Easy run 3K", "xp": 10, "type": "run", "distance": "3K", "base_pace": "7:30-8:00/km", "structure": "Steady easy pace throughout"},
            {"day": "Wed", "activity": "Strength + core (25 mins)", "xp": 15, "type": "strength", "focus": "Building", "exercises": "Squats (3x15), Push-ups (3x10-15), Side plank (3x20sec each), Single-leg glute bridges (3x10 each), Mountain climbers (3x20)"},
            {"day": "Thu", "activity": "Fartlek 3K", "xp": 15, "type": "run", "distance": "3K", "base_pace": "7:30/km easy + 6:15/km fast", "structure": "800m warm up, then 4 x (1min at 6:15/km, 2min easy), 400m cool down"},
            {"day": "Fri", "activity": "REST", "xp": 0, "type": "rest"},
            {"day": "Sat", "activity": "Parkrun 5K", "xp": 25, "type": "run", "distance": "5K", "base_pace": "6:50-7:00/km", "structure": "Aim to be 10-15 seconds faster than last week"},
            {"day": "Sun", "activity": "Long run 4K", "xp": 20, "type": "run", "distance": "4K", "base_pace": "7:45-8:00/km", "structure": "Comfortable long run pace - focus on time on feet"}
        ],
        "total_distance": "15K",
        "playlist": "Tuesday Time Travel - Pick your decade!"
    },
    3: {
        "title": "Finding Your Rhythm", 
        "activities": [
            {"day": "Mon", "activity": "REST or gentle yoga (20 mins)", "xp": 10, "type": "rest"},
            {"day": "Tue", "activity": "Easy run 3.5K", "xp": 10, "type": "run", "distance": "3.5K", "base_pace": "7:30-7:45/km", "structure": "Comfortable aerobic pace"},
            {"day": "Wed", "activity": "Strength training (25 mins)", "xp": 15, "type": "strength", "focus": "Stability", "exercises": "Lunges (3x12 each leg), Push-ups (3x12-20), Plank variations (3x45sec), Step-ups on chair (3x10 each), Dead bugs (3x10 each)"},
            {"day": "Thu", "activity": "Tempo run 3K", "xp": 15, "type": "run", "distance": "3K", "base_pace": "6:30-6:45/km tempo", "structure": "800m easy warm up, 1K at tempo pace (6:30-6:45/km), 1.2K cool down"},
            {"day": "Fri", "activity": "Easy walk/jog 2K or yoga", "xp": 10, "type": "active_recovery", "distance": "2K", "base_pace": "8:00-9:00/km", "structure": "Very easy recovery pace or walk-jog intervals"},
            {"day": "Sat", "activity": "Parkrun 5K", "xp": 25, "type": "run", "distance": "5K", "base_pace": "6:45-7:00/km", "structure": "Building confidence - aim for negative split"},
            {"day": "Sun", "activity": "Long run 4.5K", "xp": 20, "type": "run", "distance": "4.5K", "base_pace": "7:45-8:00/km", "structure": "Easy long run - enjoy the journey"}
        ],
        "total_distance": "18K",
        "playlist": "Wednesday Warriors - High-energy rock/metal"
    },
    4: {
        "title": "Stepping Up",
        "activities": [
            {"day": "Mon", "activity": "Yoga flow (20 mins)", "xp": 10, "type": "yoga"},
            {"day": "Tue", "activity": "Easy run 3.5K", "xp": 10, "type": "run", "distance": "3.5K", "base_pace": "7:30-7:45/km", "structure": "Steady aerobic effort"},
            {"day": "Wed", "activity": "Strength + core (30 mins)", "xp": 15, "type": "strength", "focus": "Power Building", "exercises": "Jump squats (3x8), Push-ups to T (3x10), Russian twists (3x20), Single-leg deadlifts (3x8 each), Burpees (3x5)"},
            {"day": "Thu", "activity": "Intervals 3.5K", "xp": 20, "type": "run", "distance": "3.5K", "base_pace": "7:30/km easy + 6:00/km intervals", "structure": "1K warm up, 4 x 400m at 6:00/km with 400m easy recovery, 700m cool down"},
            {"day": "Fri", "activity": "REST", "xp": 0, "type": "rest"},
            {"day": "Sat", "activity": "Parkrun 5K", "xp": 25, "type": "run", "distance": "5K", "base_pace": "6:40-6:55/km", "structure": "Aim for sub-35 minute finish"},
            {"day": "Sun", "activity": "Long run 5K", "xp": 25, "type": "run", "distance": "5K", "base_pace": "7:30-7:45/km", "structure": "Different route than Parkrun - explore!"}
        ],
        "total_distance": "17K",
        "playlist": "Thursday Thrills - Electronic/dance for speed"
    }
}

def adjust_pace(base_pace, adjustment):
    if not adjustment or adjustment == 0:
        return base_pace
    direction = 'faster' if adjustment > 0 else 'slower'
    magnitude = abs(adjustment)
    seconds = magnitude * 15
    return f"{base_pace} ({seconds}sec {direction} than planned)"

def get_current_week_plan(week_num, pace_adjustments):
    base_plan = WEEKLY_PLANS.get(week_num, WEEKLY_PLANS[1])
    adjusted_activities = []
    
    for activity in base_plan["activities"]:
        if activity["type"] in ["run", "active_recovery"]:
            adjustment_key = f"week{week_num}_{activity['day']}"
            adjustment = pace_adjustments.get(adjustment_key, 0)
            activity_copy = activity.copy()
            activity_copy["pace"] = adjust_pace(activity["base_pace"], adjustment)
            activity_copy["has_adjustment"] = adjustment != 0
            activity_copy["adjustment_direction"] = adjustment
            adjusted_activities.append(activity_copy)
        else:
            adjusted_activities.append(activity)
    
    return {**base_plan, "activities": adjusted_activities}

def main():
    # Initialize session state
    if 'data' not in st.session_state:
        st.session_state.data = load_data()
    
    data = st.session_state.data
    
    # Header with iPhone-friendly styling
    st.title("🏃‍♂️ 10K Quest Tracker")
    
    # Metrics in mobile-friendly layout
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total XP", data["total_xp"])
        st.metric("Current Week", f"{data['current_week']}/18")
    with col2:
        st.metric("Badges", len(data["unlocked_badges"]))
        if st.button("➕ Add Extra Workout", use_container_width=True):
            st.session_state.show_extra_workout = True
    
    # Week navigation with big buttons for iPhone
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Previous", use_container_width=True) and data["current_week"] > 1:
            data["current_week"] -= 1
            st.session_state.data = data
            save_data(data)
            st.rerun()
    with col3:
        if st.button("➡️ Next", use_container_width=True) and data["current_week"] < 18:
            data["current_week"] += 1
            st.session_state.data = data
            save_data(data)
            st.rerun()
    
    # Get current week plan
    current_plan = get_current_week_plan(data["current_week"], data["pace_adjustments"])
    
    # Week overview
    st.header(f"Week {data['current_week']}: {current_plan['title']}")
    
    # Progress tracking
    completed_this_week = sum(1 for activity in current_plan["activities"] 
                             if data["completed_activities"].get(f"week{data['current_week']}_{activity['day']}", False))
    
    progress = completed_this_week / len(current_plan["activities"])
    st.progress(progress, f"Progress: {completed_this_week}/{len(current_plan['activities'])} completed")
    
    # Playlist info
    st.info(f"🎵 **This Week's Playlist:** {current_plan['playlist']}")
    
    # Activities with mobile-friendly cards
    st.subheader("This Week's Activities")
    
    for activity in current_plan["activities"]:
        key = f"week{data['current_week']}_{activity['day']}"
        is_completed = data["completed_activities"].get(key, False)
        
        # Create a card-like container
        with st.container():
            # Main activity info
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Activity title
                title = f"**{activity['day']}: {activity['activity']}**"
                if activity.get("has_adjustment"):
                    direction = "📈" if activity["adjustment_direction"] > 0 else "📉"
                    title += f" {direction}"
                st.markdown(title)
                
                # Show completion status
                if is_completed:
                    if key in data["run_data"]:
                        run_info = data["run_data"][key]
                        feeling_emoji = {"great": "🔥", "good": "😊", "okay": "😐", "tough": "😤", "bad": "😵"}
                        st.success(f"✅ {run_info['actual_distance']} at {run_info['actual_pace']} - Felt {feeling_emoji.get(run_info['feeling'], '😐')} {run_info['feeling']}")
                    else:
                        st.success("✅ Completed!")
            
            with col2:
                st.metric("XP", activity["xp"])
            
            # Action buttons (mobile-friendly)
            if activity["type"] in ["run", "active_recovery"]:
                if not is_completed:
                    if st.button(f"🏃‍♂️ Log {activity['day']} Run", key=f"log_{key}", use_container_width=True):
                        st.session_state.current_run = activity
                        st.session_state.current_key = key
                        st.session_state.show_run_modal = True
                        st.rerun()
                else:
                    st.success("Run logged! ✅")
            else:
                button_text = "✅ Complete" if not is_completed else "✅ Completed"
                button_type = "primary" if not is_completed else "secondary"
                
                if st.button(button_text, key=f"complete_{key}", use_container_width=True, type=button_type):
                    data["completed_activities"][key] = not is_completed
                    if not is_completed:
                        data["total_xp"] += activity["xp"]
                    else:
                        data["total_xp"] -= activity["xp"]
                    st.session_state.data = data
                    save_data(data)
                    st.rerun()
            
            # Activity details in expandable sections
            if activity["type"] in ["run", "active_recovery"]:
                with st.expander(f"🎯 Garmin Setup - {activity['day']}", expanded=False):
                    st.write(f"**Distance:** {activity['distance']}")
                    st.write(f"**Target Pace:** {activity.get('pace', activity['base_pace'])}")
                    st.write(f"**Structure:** {activity['structure']}")
            
            elif activity["type"] == "strength":
                with st.expander(f"💪 Strength Focus - {activity['day']}", expanded=False):
                    st.write(f"**Focus:** {activity.get('focus', 'General')}")
                    st.write(f"**Exercises:** {activity.get('exercises', 'See training plan')}")
            
            st.divider()
    
    # Run logging modal
    if st.session_state.get("show_run_modal", False):
        st.subheader(f"🏃‍♂️ Log Your Run: {st.session_state.current_run['activity']}")
        
        with st.form("run_log_form", clear_on_submit=True):
            actual_distance = st.text_input("Distance Completed", placeholder="e.g. 2.5K, 3.2K")
            actual_pace = st.text_input("Average Pace", placeholder="e.g. 7:30/km")
            
            feeling = st.selectbox("How did it feel?", [
                "Select feeling...",
                "🔥 Great - Felt strong, could go further",
                "😊 Good - Comfortable, on target", 
                "😐 Okay - Got through it",
                "😤 Tough - Struggled but finished",
                "😵 Bad - Really difficult"
            ])
            
            notes = st.text_area("Notes (optional)", height=100)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("📝 Log Run", use_container_width=True, type="primary"):
                    if actual_distance and actual_pace and feeling != "Select feeling...":
                        feeling_map = {
                            "🔥 Great - Felt strong, could go further": "great",
                            "😊 Good - Comfortable, on target": "good",
                            "😐 Okay - Got through it": "okay", 
                            "😤 Tough - Struggled but finished": "tough",
                            "😵 Bad - Really difficult": "bad"
                        }
                        
                        run_data_entry = {
                            "actual_distance": actual_distance,
                            "actual_pace": actual_pace,
                            "feeling": feeling_map[feeling],
                            "notes": notes
                        }
                        
                        key = st.session_state.current_key
                        data["run_data"][key] = run_data_entry
                        data["completed_activities"][key] = True
                        data["total_xp"] += st.session_state.current_run["xp"]
                        
                        # Auto-adjust future paces
                        if feeling_map[feeling] == "great":
                            for i in range(1, 4):
                                future_week = data["current_week"] + (i // 7)
                                if future_week <= 18:
                                    days = ["Tue", "Thu", "Sat", "Sun"]
                                    future_day = days[i % 4]
                                    adj_key = f"week{future_week}_{future_day}"
                                    data["pace_adjustments"][adj_key] = 1
                        
                        elif feeling_map[feeling] in ["tough", "bad"]:
                            for i in range(1, 3):
                                future_week = data["current_week"] + (i // 7)
                                if future_week <= 18:
                                    days = ["Tue", "Thu", "Sun"]
                                    future_day = days[i % 3]
                                    adj_key = f"week{future_week}_{future_day}"
                                    data["pace_adjustments"][adj_key] = -1
                        
                        st.session_state.data = data
                        save_data(data)
                        st.session_state.show_run_modal = False
                        st.success("Run logged successfully! 🎉")
                        st.rerun()
                    else:
                        st.error("Please fill in all required fields")
            
            with col2:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.session_state.show_run_modal = False
                    st.rerun()
    
    # Extra workout modal
    if st.session_state.get("show_extra_workout", False):
        st.subheader("➕ Add Extra Workout")
        
        with st.form("extra_workout_form", clear_on_submit=True):
            workout_type = st.selectbox("Workout Type", [
                "Extra Run", "Cycling", "Swimming", "Extra Strength", 
                "HIIT", "Yoga Class", "Walking", "Sports", "Other"
            ])
            
            xp_options = [
                (5, "5 XP - Light activity (20-30 mins)"),
                (10, "10 XP - Moderate activity (30-45 mins)"),
                (15, "15 XP - Good workout (45-60 mins)"),
                (20, "20 XP - Intense session (60+ mins)"),
                (25, "25 XP - Epic workout (90+ mins)")
            ]
            
            selected_xp = st.selectbox("XP Value", xp_options, format_func=lambda x: x[1])
            notes = st.text_area("Notes (optional)", height=100)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("➕ Add Workout", use_container_width=True, type="primary"):
                    new_workout = {
                        "id": len(data["extra_workouts"]) + 1,
                        "week": data["current_week"],
                        "name": workout_type,
                        "xp": selected_xp[0],
                        "notes": notes,
                        "timestamp": datetime.now().isoformat()
                    }
                    data["extra_workouts"].append(new_workout)
                    data["total_xp"] += selected_xp[0]
                    st.session_state.data = data
                    save_data(data)
                    st.session_state.show_extra_workout = False
                    st.success(f"Added {workout_type} for +{selected_xp[0]} XP! 🌟")
                    st.rerun()
            
            with col2:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.session_state.show_extra_workout = False
                    st.rerun()
    
    # Extra workouts this week
    week_extra_workouts = [w for w in data["extra_workouts"] if w["week"] == data["current_week"]]
    if week_extra_workouts:
        st.subheader("✨ Extra Workouts This Week")
        for workout in week_extra_workouts:
            st.success(f"🌟 {workout['name']} - +{workout['xp']} XP")
    
    # Weekly XP summary
    base_xp = sum(activity["xp"] for activity in current_plan["activities"] 
                  if data["completed_activities"].get(f"week{data['current_week']}_{activity['day']}", False))
    extra_xp = sum(w["xp"] for w in week_extra_workouts)
    consistency_bonus = 50 if completed_this_week == len(current_plan["activities"]) else 0
    
    total_week_xp = base_xp + extra_xp + consistency_bonus
    
    st.metric("This Week's XP", total_week_xp)
    if consistency_bonus:
        st.balloons()
        st.success("🎉 Consistency Bonus: +50 XP!")
    
    # Badges section (mobile-optimized)
    st.subheader("🏆 Achievement Badges")
    
    badges = [
        {"id": "fire_starter", "name": "Fire Starter", "icon": "🔥", "desc": "Complete first week"},
        {"id": "consistency_king", "name": "Consistency King", "icon": "👑", "desc": "Complete a full week"},
        {"id": "distance_explorer", "name": "Distance Explorer", "icon": "🗾", "desc": "Run longest distance yet"},
        {"id": "speed_demon", "name": "Speed Demon", "icon": "⚡", "desc": "Beat your target pace"},
        {"id": "extra_mile", "name": "Extra Mile", "icon": "🌟", "desc": "Add 5 extra workouts"},
        {"id": "adaptive_athlete", "name": "Adaptive Athlete", "icon": "🎯", "desc": "Adjust plan based on performance"}
    ]
    
    # Check for new badges
    new_badges = []
    if data["current_week"] == 1 and completed_this_week == len(current_plan["activities"]):
        new_badges.append("fire_starter")
    if completed_this_week == len(current_plan["activities"]):
        new_badges.append("consistency_king")
    if len(data["extra_workouts"]) >= 5:
        new_badges.append("extra_mile")
    
    # Add new badges
    for badge_id in new_badges:
        if badge_id not in data["unlocked_badges"]:
            data["unlocked_badges"].append(badge_id)
            st.session_state.data = data
            save_data(data)
    
    # Display badges in 2 columns for mobile
    col1, col2 = st.columns(2)
    for i, badge in enumerate(badges):
        with col1 if i % 2 == 0 else col2:
            if badge["id"] in data["unlocked_badges"]:
                st.success(f"{badge['icon']} **{badge['name']}**\n\n{badge['desc']}")
            else:
                st.info(f"{badge['icon']} {badge['name']}\n\n{badge['desc']}")
    
    # Plan adjustments
    if data["pace_adjustments"]:
        st.subheader("🎯 Plan Adaptations")
        st.info("Your training plan has been automatically adjusted based on your recent performance:")
        
        for key, adjustment in data["pace_adjustments"].items():
            week, day = key.replace('week', '').split('_')
            direction = "📈 Increased pace" if adjustment > 0 else "📉 Easier pace"
            seconds = abs(adjustment * 15)
            st.write(f"• Week {week} {day}: {direction} ({seconds} seconds {'faster' if adjustment > 0 else 'slower'})")
    
    # Motivational footer
    st.markdown("---")
    if data["current_week"] < 18:
        st.success(f"🎯 **Next Target:** Week {data['current_week'] + 1}")
    else:
        st.success("🏁 **Race Week!** You've made it to the end!")
    
    if completed_this_week == len(current_plan["activities"]):
        st.success("🚀 Amazing work this week! Ready for the next challenge?")
    else:
        st.info("💪 Keep going! You're doing great!")

if __name__ == "__main__":
    main()