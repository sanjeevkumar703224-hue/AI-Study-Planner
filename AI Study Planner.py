import streamlit as df
from datetime import date, timedelta
import math

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Study Planner",
    page_icon="📚",
    layout="wide"
)

# ============================================================
# SESSION STATE
# ============================================================

if "subjects" not in st.session_state:
    st.session_state.subjects = []

if "plan" not in st.session_state:
    st.session_state.plan = []

if "completed" not in st.session_state:
    st.session_state.completed = set()

# ============================================================
# HEADER
# ============================================================

st.title("📚 AI Study Planner")

st.write(
    "Create a personalized study schedule based on your "
    "subjects, difficulty, available time and exam date."
)

st.divider()

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Study Settings")

    exam_date = st.date_input(
        "Exam Date",
        min_value=date.today(),
        value=date.today() + timedelta(days=7)
    )

    hours_per_day = st.slider(
        "Available Hours / Day",
        min_value=1,
        max_value=12,
        value=4
    )

    st.write(
        f"📅 Days remaining: "
        f"**{max((exam_date - date.today()).days, 0)}**"
    )

# ============================================================
# ADD SUBJECT
# ============================================================

st.header("➕ Add Subjects")

col1, col2, col3 = st.columns([3, 2, 1])

with col1:

    subject_name = st.text_input(
        "Subject Name",
        placeholder="Example: Data Structures"
    )

with col2:

    difficulty = st.selectbox(
        "Difficulty",
        ["Easy", "Medium", "Hard"]
    )

with col3:

    importance = st.selectbox(
        "Importance",
        ["Low", "Medium", "High"]
    )

if st.button(
    "➕ Add Subject",
    type="primary"
):

    if subject_name.strip():

        st.session_state.subjects.append({
            "name": subject_name.strip(),
            "difficulty": difficulty,
            "importance": importance
        })

        st.success(
            f"{subject_name} added!"
        )

    else:

        st.warning(
            "Enter a subject name."
        )

# ============================================================
# SUBJECT LIST
# ============================================================

if st.session_state.subjects:

    st.subheader("📋 Your Subjects")

    for i, subject in enumerate(
        st.session_state.subjects
    ):

        col1, col2, col3, col4 = st.columns(
            [4, 2, 2, 1]
        )

        with col1:
            st.write(
                f"**{subject['name']}**"
            )

        with col2:
            st.write(
                subject["difficulty"]
            )

        with col3:
            st.write(
                subject["importance"]
            )

        with col4:

            if st.button(
                "❌",
                key=f"delete_{i}"
            ):

                st.session_state.subjects.pop(i)
                st.rerun()

else:

    st.info(
        "Add at least one subject to create your study plan."
    )

# ============================================================
# PRIORITY CALCULATION
# ============================================================

def calculate_priority(subject):

    difficulty_score = {
        "Easy": 1,
        "Medium": 2,
        "Hard": 3
    }

    importance_score = {
        "Low": 1,
        "Medium": 2,
        "High": 3
    }

    return (
        difficulty_score[subject["difficulty"]]
        *
        importance_score[subject["importance"]]
    )

# ============================================================
# GENERATE PLAN
# ============================================================

st.divider()

if st.button(
    "🧠 Generate AI Study Plan",
    type="primary",
    use_container_width=True
):

    if not st.session_state.subjects:

        st.error(
            "Please add subjects first."
        )

    else:

        days = max(
            (exam_date - date.today()).days,
            1
        )

        subjects = sorted(
            st.session_state.subjects,
            key=calculate_priority,
            reverse=True
        )

        total_priority = sum(
            calculate_priority(s)
            for s in subjects
        )

        plan = []

        for day_number in range(1, days + 1):

            current_date = (
                date.today()
                + timedelta(days=day_number - 1)
            )

            remaining_hours = hours_per_day

            daily_tasks = []

            for subject in subjects:

                priority = calculate_priority(
                    subject
                )

                allocated = (
                    hours_per_day
                    *
                    priority
                    /
                    total_priority
                )

                allocated = max(
                    0.5,
                    round(allocated * 2) / 2
                )

                allocated = min(
                    allocated,
                    remaining_hours
                )

                if allocated <= 0:
                    continue

                daily_tasks.append({
                    "subject": subject["name"],
                    "hours": allocated,
                    "difficulty": subject["difficulty"]
                })

                remaining_hours -= allocated

                if remaining_hours <= 0:
                    break

            plan.append({
                "day": day_number,
                "date": current_date,
                "tasks": daily_tasks
            })

        st.session_state.plan = plan
        st.session_state.completed = set()

        st.success(
            "🎉 Your personalized study plan is ready!"
        )

# ============================================================
# DISPLAY PLAN
# ============================================================

if st.session_state.plan:

    st.divider()

    st.header("📅 Your Study Plan")

    total_days = len(
        st.session_state.plan
    )

    completed_count = len(
        st.session_state.completed
    )

    total_tasks = sum(
        len(day["tasks"])
        for day in st.session_state.plan
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Study Days",
            total_days
        )

    with col2:

        st.metric(
            "Total Tasks",
            total_tasks
        )

    with col3:

        st.metric(
            "Completed",
            completed_count
        )

    progress = (
        completed_count / total_tasks
        if total_tasks
        else 0
    )

    st.progress(
        progress
    )

    st.write(
        f"Overall Progress: "
        f"**{progress * 100:.0f}%**"
    )

    # ========================================================
    # DAILY PLAN
    # ========================================================

    for day in st.session_state.plan:

        day_title = (
            f"Day {day['day']} — "
            f"{day['date'].strftime('%d %b %Y')}"
        )

        with st.expander(
            day_title,
            expanded=day["day"] == 1
        ):

            for task_index, task in enumerate(
                day["tasks"]
            ):

                task_id = (
                    f"{day['day']}_"
                    f"{task_index}"
                )

                completed = (
                    task_id
                    in st.session_state.completed
                )

                col1, col2, col3 = st.columns(
                    [5, 2, 1]
                )

                with col1:

                    if completed:

                        st.write(
                            f"~~{task['subject']}~~"
                        )

                    else:

                        st.write(
                            f"📖 **{task['subject']}**"
                        )

                with col2:

                    st.write(
                        f"{task['hours']} hours"
                    )

                with col3:

                    if st.checkbox(
                        "Done",
                        value=completed,
                        key=f"done_{task_id}"
                    ):

                        st.session_state.completed.add(
                            task_id
                        )

                    else:

                        st.session_state.completed.discard(
                            task_id
                        )

# ============================================================
# STUDY ADVICE
# ============================================================

st.divider()

st.header("💡 Smart Study Recommendations")

recommendations = [
    (
        "🧠 Active Recall",
        "Close your notes and try to recall concepts from memory."
    ),
    (
        "💻 Coding Practice",
        "After learning a programming topic, solve at least 2–3 problems."
    ),
    (
        "🔄 Revision",
        "Review difficult topics repeatedly instead of studying them once."
    ),
    (
        "⏱️ Pomodoro",
        "Study for 50 minutes followed by a 10-minute break."
    ),
    (
        "📝 Mock Tests",
        "Take a timed test regularly to measure your actual performance."
    )
]

for title, description in recommendations:

    with st.expander(title):

        st.write(description)

# ============================================================
# DOWNLOAD PLAN
# ============================================================

if st.session_state.plan:

    report = []

    report.append("AI STUDY PLANNER")
    report.append("=" * 40)
    report.append("")

    report.append(
        f"Exam Date: {exam_date}"
    )

    report.append(
        f"Hours Per Day: {hours_per_day}"
    )

    report.append("")

    for day in st.session_state.plan:

        report.append(
            f"DAY {day['day']} - {day['date']}"
        )

        for task in day["tasks"]:

            report.append(
                f"  {task['subject']} - "
                f"{task['hours']} hours"
            )

        report.append("")

    st.download_button(
        "⬇️ Download Study Plan",
        "\n".join(report),
        file_name="ai_study_plan.txt",
        mime="text/plain"
    )

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Study Planner • Built with Python + Streamlit"
)
