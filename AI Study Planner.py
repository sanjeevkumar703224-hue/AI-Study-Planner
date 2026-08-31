import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date, timedelta
import random
import math
import time

DB = "ai_study_planner.db"

st.set_page_config(
    page_title="AI Study Planner",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(99,102,241,.12), transparent 25%),
        radial-gradient(circle at 90% 20%, rgba(168,85,247,.10), transparent 25%),
        linear-gradient(135deg, #070b18, #0c1020 50%, #090d19);
    color: #f8fafc;
}

.block-container {
    padding-top: 2rem;
    max-width: 1450px;
}

.hero {
    padding: 35px;
    border-radius: 28px;
    background: linear-gradient(135deg, rgba(30,41,80,.9), rgba(15,23,42,.85));
    border: 1px solid rgba(148,163,184,.18);
    box-shadow: 0 25px 80px rgba(0,0,0,.3);
    margin-bottom: 25px;
}

.hero h1 {
    font-size: 46px;
    font-weight: 800;
    margin-bottom: 5px;
}

.hero p {
    color: #a5b4fc;
    font-size: 17px;
}

.card {
    background: rgba(15,23,42,.72);
    border: 1px solid rgba(148,163,184,.15);
    border-radius: 22px;
    padding: 22px;
    box-shadow: 0 15px 40px rgba(0,0,0,.20);
}

.metric {
    background: linear-gradient(135deg, rgba(30,41,80,.8), rgba(15,23,42,.8));
    border: 1px solid rgba(148,163,184,.13);
    border-radius: 20px;
    padding: 20px;
    text-align: center;
}

.metric h2 {
    font-size: 34px;
    margin: 0;
}

.metric p {
    color: #94a3b8;
    margin: 5px 0 0;
}

.badge {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    background: rgba(99,102,241,.18);
    color: #c7d2fe;
    font-size: 12px;
    font-weight: 700;
}

.ai-box {
    padding: 22px;
    border-radius: 22px;
    background: linear-gradient(135deg, rgba(79,70,229,.16), rgba(168,85,247,.12));
    border: 1px solid rgba(129,140,248,.25);
}

.task {
    padding: 17px;
    border-radius: 18px;
    background: rgba(30,41,59,.6);
    border: 1px solid rgba(148,163,184,.12);
    margin-bottom: 10px;
}

.success {
    color: #86efac;
}

.warning {
    color: #fde68a;
}

.danger {
    color: #fca5a5;
}

div[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080d1d, #0d1326);
    border-right: 1px solid rgba(148,163,184,.1);
}

button[kind="primary"] {
    border-radius: 12px;
}

.stProgress > div > div > div > div {
    border-radius: 20px;
}
</style>
""", unsafe_allow_html=True)


def db():
    return sqlite3.connect(DB, check_same_thread=False)


def init_db():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            title TEXT,
            difficulty INTEGER,
            priority INTEGER,
            minutes INTEGER,
            deadline TEXT,
            completed INTEGER DEFAULT 0,
            created TEXT,
            completed_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            minutes INTEGER,
            session_date TEXT,
            focus INTEGER
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            exam_date TEXT,
            importance INTEGER
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


def add_task(subject, title, difficulty, priority, minutes, deadline):
    conn = db()
    conn.execute("""
        INSERT INTO tasks
        (subject,title,difficulty,priority,minutes,deadline,created)
        VALUES (?,?,?,?,?,?,?)
    """, (
        subject,
        title,
        difficulty,
        priority,
        minutes,
        deadline,
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()


def get_tasks():
    conn = db()
    df = pd.read_sql_query(
        "SELECT * FROM tasks ORDER BY completed ASC, priority DESC, deadline ASC",
        conn
    )
    conn.close()
    return df


def complete_task(task_id):
    conn = db()
    conn.execute(
        "UPDATE tasks SET completed=1, completed_at=? WHERE id=?",
        (datetime.now().isoformat(), task_id)
    )
    conn.commit()
    conn.close()


def delete_task(task_id):
    conn = db()
    conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()


def add_session(subject, minutes, focus):
    conn = db()
    conn.execute("""
        INSERT INTO sessions(subject,minutes,session_date,focus)
        VALUES(?,?,?,?)
    """, (
        subject,
        minutes,
        date.today().isoformat(),
        focus
    ))
    conn.commit()
    conn.close()


def get_sessions():
    conn = db()
    df = pd.read_sql_query(
        "SELECT * FROM sessions ORDER BY session_date",
        conn
    )
    conn.close()
    return df


def add_exam(subject, exam_date, importance):
    conn = db()
    conn.execute(
        "INSERT INTO exams(subject,exam_date,importance) VALUES(?,?,?)",
        (subject, exam_date, importance)
    )
    conn.commit()
    conn.close()


def get_exams():
    conn = db()
    df = pd.read_sql_query(
        "SELECT * FROM exams ORDER BY exam_date",
        conn
    )
    conn.close()
    return df


def calculate_streak():
    sessions = get_sessions()

    if sessions.empty:
        return 0

    days = set(pd.to_datetime(sessions["session_date"]).dt.date)

    streak = 0
    current = date.today()

    while current in days:
        streak += 1
        current -= timedelta(days=1)

    return streak


def calculate_focus_score():
    sessions = get_sessions()

    if sessions.empty:
        return 0

    recent = sessions.tail(20)

    weighted = (
        recent["focus"] * recent["minutes"]
    ).sum()

    total = recent["minutes"].sum()

    if total == 0:
        return 0

    return round(weighted / total)


def ai_score_task(row):
    score = 0

    score += row["difficulty"] * 20
    score += row["priority"] * 25

    try:
        deadline = datetime.fromisoformat(row["deadline"]).date()
        days = (deadline - date.today()).days

        if days <= 0:
            score += 80
        elif days <= 2:
            score += 60
        elif days <= 5:
            score += 40
        elif days <= 10:
            score += 20
    except:
        pass

    return score


def generate_ai_plan(tasks, available_minutes):
    if tasks.empty:
        return []

    pending = tasks[tasks["completed"] == 0].copy()

    if pending.empty:
        return []

    pending["ai_score"] = pending.apply(ai_score_task, axis=1)
    pending = pending.sort_values("ai_score", ascending=False)

    plan = []
    remaining = available_minutes

    for _, row in pending.iterrows():

        if remaining <= 0:
            break

        duration = min(int(row["minutes"]), remaining)

        if duration < 15:
            continue

        plan.append({
            "subject": row["subject"],
            "title": row["title"],
            "minutes": duration,
            "score": int(row["ai_score"])
        })

        remaining -= duration

    return plan


def study_recommendation():
    tasks = get_tasks()
    sessions = get_sessions()

    if tasks.empty:
        return "Add your subjects and study tasks. The AI planner will automatically prioritize them."

    pending = tasks[tasks["completed"] == 0]

    if pending.empty:
        return "Excellent! Your task list is clear. Use this time for revision, mock tests, or advanced learning."

    urgent = 0

    for _, row in pending.iterrows():
        try:
            deadline = datetime.fromisoformat(row["deadline"]).date()
            if (deadline - date.today()).days <= 2:
                urgent += 1
        except:
            pass

    if urgent >= 3:
        return f"You have {urgent} urgent tasks. Focus on deadline-driven work before starting new topics."

    if not sessions.empty:
        avg_focus = sessions["focus"].tail(10).mean()

        if avg_focus < 55:
            return "Your recent focus score is low. Try 25-minute distraction-free Pomodoro sessions."

        if avg_focus > 85:
            return "Your focus performance is excellent. You can safely increase difficult-topic study blocks."

    hardest = pending.sort_values("difficulty", ascending=False).iloc[0]

    return f"Recommended next: {hardest['title']} from {hardest['subject']}. It has a difficulty score of {hardest['difficulty']}/5."


def initialize_demo():
    if not get_tasks().empty:
        return

    today = date.today()

    demo = [
        ("Python", "Advanced Functions & Decorators", 4, 5, 60, 3),
        ("DSA", "Binary Search Problems", 4, 5, 75, 2),
        ("Machine Learning", "Linear Regression", 3, 4, 60, 5),
        ("AI", "Neural Networks Fundamentals", 5, 5, 90, 7),
        ("Communication", "Interview Speaking Practice", 2, 3, 30, 10)
    ]

    for subject, title, diff, priority, minutes, days in demo:
        add_task(
            subject,
            title,
            diff,
            priority,
            minutes,
            (today + timedelta(days=days)).isoformat()
        )


initialize_demo()


if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "pomodoro_running" not in st.session_state:
    st.session_state.pomodoro_running = False

if "pomodoro_seconds" not in st.session_state:
    st.session_state.pomodoro_seconds = 25 * 60


with st.sidebar:

    st.markdown("""
    <div style="text-align:center;padding:20px 0;">
        <div style="font-size:55px;">🧠</div>
        <h2>AI STUDY OS</h2>
        <span class="badge">SMART LEARNING ENGINE</span>
    </div>
    """, unsafe_allow_html=True)

    pages = [
        "Dashboard",
        "AI Planner",
        "Tasks",
        "Pomodoro",
        "Analytics",
        "Exams",
        "AI Coach"
    ]

    for p in pages:
        if st.button(
            p,
            use_container_width=True,
            type="primary" if st.session_state.page == p else "secondary"
        ):
            st.session_state.page = p
            st.rerun()

    st.markdown("---")

    st.markdown("### ⚡ System Status")
    st.success("AI Engine Online")
    st.success("Database Connected")
    st.success("Planner Ready")

    st.markdown("---")
    st.caption("AI Study Planner v1.0")
    st.caption("Single-file intelligent learning system")


tasks = get_tasks()
sessions = get_sessions()
exams = get_exams()

completed = int(tasks["completed"].sum()) if not tasks.empty else 0
total_tasks = len(tasks)
completion_rate = round((completed / total_tasks) * 100) if total_tasks else 0
total_minutes = int(sessions["minutes"].sum()) if not sessions.empty else 0
streak = calculate_streak()
focus_score = calculate_focus_score()


if st.session_state.page == "Dashboard":

    st.markdown("""
    <div class="hero">
        <span class="badge">AI-POWERED PERSONAL LEARNING SYSTEM</span>
        <h1>Welcome to your Study Command Center 🚀</h1>
        <p>
        Plan smarter. Study deeper. Track everything.
        Your adaptive learning engine is ready.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.markdown(
            f'<div class="metric"><h2>{completion_rate}%</h2><p>Completion</p></div>',
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f'<div class="metric"><h2>{total_minutes}</h2><p>Study Minutes</p></div>',
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f'<div class="metric"><h2>{streak} 🔥</h2><p>Day Streak</p></div>',
            unsafe_allow_html=True
        )

    with c4:
        st.markdown(
            f'<div class="metric"><h2>{focus_score}%</h2><p>Focus Score</p></div>',
            unsafe_allow_html=True
        )

    with c5:
        st.markdown(
            f'<div class="metric"><h2>{len(exams)}</h2><p>Exams</p></div>',
            unsafe_allow_html=True
        )

    st.write("")

    left, right = st.columns([1.4, 1])

    with left:

        st.markdown("### 🤖 AI Daily Intelligence")

        st.markdown(
            f"""
            <div class="ai-box">
                <span class="badge">AI RECOMMENDATION</span>
                <h3>Today's Learning Strategy</h3>
                <p>{study_recommendation()}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")

        st.markdown("### 📋 Priority Tasks")

        pending = tasks[tasks["completed"] == 0].copy()

        if not pending.empty:

            pending["AI Priority"] = pending.apply(ai_score_task, axis=1)
            pending = pending.sort_values(
                "AI Priority",
                ascending=False
            ).head(5)

            for _, row in pending.iterrows():

                deadline = row["deadline"]

                st.markdown(
                    f"""
                    <div class="task">
                        <b>{row['title']}</b><br>
                        <span style="color:#a5b4fc">{row['subject']}</span>
                        &nbsp; • &nbsp;
                        {row['minutes']} min
                        &nbsp; • &nbsp;
                        Priority {row['priority']}/5
                        <br>
                        <small>Deadline: {deadline}</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        else:
            st.success("All tasks completed 🎉")

    with right:

        st.markdown("### 🎯 Today's Target")

        target = st.slider(
            "Daily study target",
            30,
            600,
            180,
            15
        )

        today_minutes = 0

        if not sessions.empty:
            today_minutes = int(
                sessions[
                    sessions["session_date"] == date.today().isoformat()
                ]["minutes"].sum()
            )

        progress = min(today_minutes / target, 1)

        st.progress(progress)

        st.markdown(
            f"""
            <div class="card">
                <h2>{today_minutes} / {target} min</h2>
                <p>Today's study progress</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")

        st.markdown("### 🧠 Productivity Level")

        if focus_score >= 85:
            st.success("Elite Focus")
        elif focus_score >= 65:
            st.info("Strong Focus")
        elif focus_score >= 40:
            st.warning("Needs Improvement")
        else:
            st.error("Critical Focus Recovery Needed")


elif st.session_state.page == "AI Planner":

    st.markdown("""
    <div class="hero">
        <span class="badge">ADAPTIVE AI ENGINE</span>
        <h1>🤖 AI Study Planner</h1>
        <p>Automatically generate today's optimal study sequence.</p>
    </div>
    """, unsafe_allow_html=True)

    available = st.slider(
        "How much time do you have today?",
        30,
        600,
        180,
        15
    )

    if st.button(
        "⚡ GENERATE INTELLIGENT STUDY PLAN",
        type="primary",
        use_container_width=True
    ):

        plan = generate_ai_plan(tasks, available)

        if not plan:
            st.warning("No suitable pending tasks found.")
        else:

            total = sum(x["minutes"] for x in plan)

            st.success(
                f"AI generated a {total}-minute optimized study plan."
            )

            for index, item in enumerate(plan, 1):

                st.markdown(
                    f"""
                    <div class="task">
                        <span class="badge">BLOCK {index}</span>
                        <h3>{item['title']}</h3>
                        <p>
                        📚 {item['subject']}
                        &nbsp;&nbsp; ⏱️ {item['minutes']} minutes
                        &nbsp;&nbsp; 🧠 AI Score {item['score']}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("### 🧬 AI Strategy")

            strategies = [
                "Start with the highest cognitive-load topic while your brain is fresh.",
                "Use active recall instead of passive reading.",
                "Finish every block with 5 minutes of self-testing.",
                "Keep your phone away during deep-work sessions.",
                "After difficult topics, switch to a lighter subject to prevent fatigue."
            ]

            st.info(random.choice(strategies))


elif st.session_state.page == "Tasks":

    st.markdown("""
    <div class="hero">
        <span class="badge">TASK MANAGEMENT</span>
        <h1>📋 Smart Task Matrix</h1>
        <p>Create, prioritize and complete your learning missions.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("➕ Create New Study Mission", expanded=True):

        a, b = st.columns(2)

        with a:
            subject = st.text_input(
                "Subject",
                placeholder="e.g. Python"
            )

            title = st.text_input(
                "Task",
                placeholder="e.g. Master Dynamic Programming"
            )

            minutes = st.number_input(
                "Estimated Minutes",
                min_value=10,
                max_value=600,
                value=60,
                step=10
            )

        with b:
            difficulty = st.slider(
                "Difficulty",
                1,
                5,
                3
            )

            priority = st.slider(
                "Priority",
                1,
                5,
                3
            )

            deadline = st.date_input(
                "Deadline",
                date.today() + timedelta(days=3)
            )

        if st.button(
            "CREATE MISSION",
            type="primary"
        ):
            if subject and title:
                add_task(
                    subject,
                    title,
                    difficulty,
                    priority,
                    minutes,
                    deadline.isoformat()
                )
                st.success("Mission created successfully.")
                time.sleep(.5)
                st.rerun()
            else:
                st.error("Enter subject and task name.")

    st.markdown("### 🗂️ Mission Database")

    tasks = get_tasks()

    if tasks.empty:
        st.info("No tasks available.")
    else:

        for _, row in tasks.iterrows():

            status = "✅ COMPLETED" if row["completed"] else "⏳ PENDING"

            col1, col2, col3 = st.columns([5, 1, 1])

            with col1:
                st.markdown(
                    f"""
                    <div class="task">
                        <b>{row['title']}</b>
                        <br>
                        <span style="color:#a5b4fc">
                        {row['subject']}
                        </span>
                        <br>
                        ⏱️ {row['minutes']} min
                        &nbsp; • &nbsp;
                        Difficulty {row['difficulty']}/5
                        &nbsp; • &nbsp;
                        Priority {row['priority']}/5
                        &nbsp; • &nbsp;
                        {status}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col2:
                if not row["completed"]:
                    if st.button(
                        "Complete",
                        key=f"complete_{row['id']}"
                    ):
                        complete_task(row["id"])
                        st.rerun()

            with col3:
                if st.button(
                    "Delete",
                    key=f"delete_{row['id']}"
                ):
                    delete_task(row["id"])
                    st.rerun()


elif st.session_state.page == "Pomodoro":

    st.markdown("""
    <div class="hero">
        <span class="badge">DEEP WORK ENGINE</span>
        <h1>⏱️ AI Pomodoro</h1>
        <p>Turn study time into measurable high-focus sessions.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        work_minutes = st.number_input(
            "Focus duration",
            5,
            120,
            25
        )

    with c2:
        subject = st.text_input(
            "Study subject",
            "Deep Work"
        )

    with c3:
        focus = st.slider(
            "Expected focus",
            1,
            100,
            85
        )

    st.markdown(
        f"""
        <div class="card" style="text-align:center;">
            <h1 style="font-size:90px;">
                {st.session_state.pomodoro_seconds // 60:02d}:
                {st.session_state.pomodoro_seconds % 60:02d}
            </h1>
            <p>FOCUS MODE</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(
            "▶ START",
            type="primary",
            use_container_width=True
        ):
            st.session_state.pomodoro_running = True

    with col2:
        if st.button(
            "⏸ PAUSE",
            use_container_width=True
        ):
            st.session_state.pomodoro_running = False

    with col3:
        if st.button(
            "↻ RESET",
            use_container_width=True
        ):
            st.session_state.pomodoro_running = False
            st.session_state.pomodoro_seconds = work_minutes * 60
            st.rerun()

    if st.session_state.pomodoro_running:

        if st.session_state.pomodoro_seconds > 0:

            time.sleep(1)

            st.session_state.pomodoro_seconds -= 1
            st.rerun()

        else:

            st.session_state.pomodoro_running = False

            add_session(
                subject,
                work_minutes,
                focus
            )

            st.success(
                "🎉 Focus session complete! Session saved."
            )

            st.session_state.pomodoro_seconds = work_minutes * 60


elif st.session_state.page == "Analytics":

    st.markdown("""
    <div class="hero">
        <span class="badge">PERFORMANCE INTELLIGENCE</span>
        <h1>📊 Learning Analytics</h1>
        <p>Understand exactly how you are spending your learning time.</p>
    </div>
    """, unsafe_allow_html=True)

    sessions = get_sessions()

    if sessions.empty:

        st.info(
            "Complete Pomodoro sessions to generate analytics."
        )

    else:

        sessions["date"] = pd.to_datetime(
            sessions["session_date"]
        )

        daily = sessions.groupby("date")["minutes"].sum().reset_index()

        fig = px.area(
            daily,
            x="date",
            y="minutes",
            title="Daily Study Time"
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        left, right = st.columns(2)

        with left:

            subject_data = sessions.groupby(
                "subject"
            )["minutes"].sum().reset_index()

            fig2 = px.pie(
                subject_data,
                names="subject",
                values="minutes",
                title="Study Distribution"
            )

            fig2.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

        with right:

            focus_data = sessions.groupby(
                "subject"
            )["focus"].mean().reset_index()

            fig3 = px.bar(
                focus_data,
                x="subject",
                y="focus",
                title="Average Focus by Subject"
            )

            fig3.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(
                fig3,
                use_container_width=True
            )

        st.markdown("### 🧠 AI Performance Analysis")

        avg_focus = sessions["focus"].mean()
        avg_minutes = sessions.groupby("session_date")["minutes"].sum().mean()

        if avg_focus >= 85:
            analysis = "Elite focus consistency. Increase difficulty gradually."
        elif avg_focus >= 65:
            analysis = "Good focus performance. Increase uninterrupted study blocks."
        else:
            analysis = "Focus consistency needs improvement. Use shorter distraction-free blocks."

        st.markdown(
            f"""
            <div class="ai-box">
                <h3>AI Diagnosis</h3>
                <p>
                Average focus: <b>{avg_focus:.1f}%</b><br>
                Average daily study time: <b>{avg_minutes:.1f} min</b><br><br>
                {analysis}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )


elif st.session_state.page == "Exams":

    st.markdown("""
    <div class="hero">
        <span class="badge">EXAM INTELLIGENCE</span>
        <h1>🎯 Exam Command Center</h1>
        <p>Track upcoming exams and automatically identify urgency.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("➕ Add Examination"):

        subject = st.text_input(
            "Exam Subject"
        )

        exam_date = st.date_input(
            "Exam Date",
            date.today() + timedelta(days=7)
        )

        importance = st.slider(
            "Importance",
            1,
            5,
            5
        )

        if st.button(
            "ADD EXAM",
            type="primary"
        ):
            if subject:
                add_exam(
                    subject,
                    exam_date.isoformat(),
                    importance
                )
                st.success("Exam added.")
                st.rerun()

    exams = get_exams()

    st.markdown("### 📅 Upcoming Exams")

    if exams.empty:

        st.info("No exams scheduled.")

    else:

        for _, exam in exams.iterrows():

            exam_day = datetime.fromisoformat(
                exam["exam_date"]
            ).date()

            days_left = (exam_day - date.today()).days

            if days_left < 0:
                label = "COMPLETED"
            elif days_left == 0:
                label = "TODAY 🔥"
            elif days_left <= 3:
                label = "URGENT ⚠️"
            elif days_left <= 7:
                label = "HIGH PRIORITY"
            else:
                label = "PLANNED"

            st.markdown(
                f"""
                <div class="task">
                    <span class="badge">{label}</span>
                    <h2>{exam['subject']}</h2>
                    <p>
                    📅 {exam['exam_date']}
                    &nbsp;&nbsp;
                    ⏳ {max(days_left, 0)} days remaining
                    &nbsp;&nbsp;
                    ⭐ Importance {exam['importance']}/5
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )


elif st.session_state.page == "AI Coach":

    st.markdown("""
    <div class="hero">
        <span class="badge">PERSONAL AI MENTOR</span>
        <h1>🧠 AI Study Coach</h1>
        <p>Your intelligent learning strategy assistant.</p>
    </div>
    """, unsafe_allow_html=True)

    question = st.text_area(
        "Ask your AI Study Coach",
        placeholder="Example: I have 3 hours today. What should I study?"
    )

    if st.button(
        "ASK AI COACH",
        type="primary",
        use_container_width=True
    ):

        q = question.lower()

        if not q:
            st.warning("Ask something first.")

        elif "3 hour" in q or "3 hours" in q:
            st.success(
                "Recommended structure: 60 min hardest topic → "
                "15 min break → 60 min problem solving → "
                "15 min break → 30 min revision."
            )

        elif "tired" in q or "burnout" in q:
            st.info(
                "Reduce cognitive load. Use a 25-minute light revision "
                "block, take a proper break, hydrate, then reassess."
            )

        elif "python" in q:
            st.success(
                "Use a progression of concept → guided example → "
                "independent problem → debugging → mini-project."
            )

        elif "dsa" in q:
            st.success(
                "Prioritize patterns over random problems: arrays, "
                "hashing, two pointers, binary search, stacks, trees, "
                "graphs and dynamic programming."
            )

        elif "exam" in q:
            st.warning(
                "Use an exam-first strategy: identify high-weight topics, "
                "practice active recall, solve previous questions, "
                "then perform timed mock tests."
            )

        else:
            st.markdown(
                """
                <div class="ai-box">
                    <h3>🤖 AI Coach Analysis</h3>
                    <p>
                    Your question has been processed through the
                    Study Intelligence Engine.
                    </p>
                    <p>
                    Recommended principle:
                    <b>Learn → Recall → Practice → Test → Analyze → Repeat.</b>
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.write("")

    st.markdown("### ⚡ Quick Coaching Modes")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
            <div class="card">
            <h3>🎯 Focus Mode</h3>
            <p>Remove distractions and complete one task at a time.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            """
            <div class="card">
            <h3>🧠 Memory Mode</h3>
            <p>Use active recall and spaced repetition.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            """
            <div class="card">
            <h3>⚔️ Interview Mode</h3>
            <p>Practice coding, explanation and timed problem solving.</p>
            </div>
            """,
            unsafe_allow_html=True
        )


st.markdown("---")

st.markdown(
    """
    <div style="text-align:center;color:#64748b;padding:20px;">
        🧠 AI Study Planner • Adaptive Learning OS •
        Built with Python + Streamlit + SQLite + Plotly
    </div>
    """,
    unsafe_allow_html=True
)
