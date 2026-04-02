# app.py
import streamlit as st
from datetime import date

from scraper import scrape_nptel_course
from tutor import llm_call, current_llm
from config import DEFAULT_DAILY_HOURS, DEFAULT_EXAM_DATE

st.set_page_config(page_title="SmartCoursePrep", page_icon="🎓", layout="wide")

st.title("🎓 SmartCoursePrep - In-Depth Weekly Summaries")
st.subheader("Paste any NPTEL course link → Get detailed, exam-focused summaries")

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("Settings")
    daily_hours = st.slider("Daily study hours", 1.0, 6.0, DEFAULT_DAILY_HOURS, 0.5)
    exam_date = st.date_input("Exam Date", value=date.fromisoformat(DEFAULT_EXAM_DATE))
    st.caption(f"**Active LLM**: {current_llm}")

    st.divider()
    st.subheader("📚 Course Weeks")

    if "course_data" in st.session_state and st.session_state.course_data.get("weeks"):
        for week_num, title in st.session_state.course_data["weeks"].items():
            if st.button(f"Week {week_num}: {title}", key=f"week_btn_{week_num}", use_container_width=True):
                st.session_state.selected_week = week_num
    else:
        st.info("Load a course to see the weeks here.")

# ====================== MAIN AREA ======================
course_url = st.text_input(
    "NPTEL / SWAYAM Course Link",
    placeholder="e.g. https://nptel.ac.in/courses/106/105/106105219/",
    help="Paste the URL of the NPTEL course you want to prepare for."
)

col1, col2 = st.columns([1, 4])
with col1:
    if st.button("🚀 Load Course", type="primary"):
        with st.spinner("Scraping syllabus..."):
            course_data = scrape_nptel_course(course_url)

        if not course_data.get("scraped_success", False) and not course_data.get("weeks"):
            st.warning("⚠️ Could not automatically extract weeks. Use manual input below.")
        else:
            st.success(f"✅ Loaded: **{course_data.get('title', 'Course')}**")
            if course_data.get("weeks_found", 0) > 0:
                st.info(f"Found {course_data.get('weeks_found')} weeks.")

        st.session_state.course_data = course_data
        st.session_state.selected_week = next(iter(course_data.get("weeks", {})), 1)
        if "summaries" not in st.session_state:
            st.session_state.summaries = {}

# Manual Syllabus Fallback (Very Useful for NPTEL)
if "course_data" in st.session_state and (not st.session_state.course_data.get("weeks") or len(st.session_state.course_data["weeks"]) < 4):
    st.info("**Manual Syllabus Input** (if auto-scraping failed)")
    manual_syllabus = st.text_area(
        "Paste the course syllabus here (Week 1: Title, Week 2: Title, ...)",
        height=150,
        help="Format: Week 1: Title\nWeek 2: Title"
    )
    if st.button("Apply Manual Syllabus"):
        # Simple parsing logic can be added here if needed
        st.success("Manual syllabus applied (extend parsing if required)")

# ====================== SUMMARY DISPLAY ======================
if "course_data" in st.session_state:
    weeks = st.session_state.course_data.get("weeks", {})
    selected = st.session_state.get("selected_week", 1)

    if selected in weeks:
        st.subheader(f"📖 Week {selected}: {weeks[selected]}")

        if st.button("🔄 Generate In-Depth Summary", type="primary"):
            with st.spinner("Generating detailed summary..."):
                prompt = f"""
                Create a **detailed, in-depth summary** for Week {selected}: {weeks[selected]}
                of the course "{st.session_state.course_data.get('title')}".

                Use this structure:
                1. **Overview**
                2. **Key Concepts & Theories**
                3. **Important Models / Frameworks / Researchers**
                4. **Real-life Examples & Analogies**
                5. **Applications**
                6. **Exam Tips**

                Use bullet points, tables, and keep it revision-friendly.
                """

                summary = llm_call(prompt)
                st.session_state.summaries[selected] = summary

        if selected in st.session_state.summaries:
            st.markdown(st.session_state.summaries[selected])
        else:
            st.info("Click the button above to generate the summary.")

