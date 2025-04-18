import streamlit as st
import google.generativeai as genai
import PyPDF2
import random

genai.configure(api_key="your api here")  
model = genai.GenerativeModel("gemini-2.0-flash")

#  SIDEBAR NAVIGATION 
st.set_page_config(page_title="📘 Study Companion")
st.sidebar.title("🧭 Navigation")
app = st.sidebar.radio("Choose a feature:", ["📚 Study Notes & Quiz", "🤝 Find Project Partner"])

# ============ FEATURE 1: STUDY NOTES & QUIZ ============
if app == "📚 Study Notes & Quiz":
    st.title("📖 Study Buddy")
    st.write("Choose to upload a PDF or enter a topic to get a structured explanation, summary, and quiz!")

    tab1, tab2 = st.tabs(["📄 Upload PDF", "📝 Enter Topic"])

    # --- PDF Upload Tab ---
    with tab1:
        st.subheader("📄 Upload a PDF")
        uploaded_file = st.file_uploader("Upload your PDF file", type=["pdf"])

        if uploaded_file is not None:
            with st.spinner("📖 Reading your PDF..."):
                reader = PyPDF2.PdfReader(uploaded_file)
                full_text = ""
                for page in reader.pages:
                    full_text += page.extract_text()

                max_chars = 8000
                truncated_text = full_text[:max_chars]

            st.success("✅ PDF read successfully!")

            if truncated_text.strip():
                with st.spinner("🧠 Generating study material with Gemini..."):
                    explain_prompt = f"""Explain the following study material in simple terms:

{truncated_text}"""
                    summary_prompt = f"""Summarize the following content in around 100 words:

{truncated_text}"""
                    quiz_prompt = (
                        f"Create 5 multiple choice questions with 4 options each (A, B, C, D) based on the following content.\n"
                        f"At the end, provide the correct answers in this format: Answers: 1. B 2. C 3. A 4. D 5. B\n\n{truncated_text}"
                    )

                    explanation = model.generate_content(explain_prompt).text
                    summary = model.generate_content(summary_prompt).text
                    quiz = model.generate_content(quiz_prompt).text

                st.subheader("📖 Explanation")
                st.write(explanation)

                st.subheader("📘 Summary")
                st.write(summary)

                st.subheader("🧠 Quiz")
                st.markdown(quiz)
            else:
                st.error("❌ Could not extract any readable text from the PDF.")

    # --- Topic Entry Tab ---
    with tab2:
        st.subheader("📝 Type a Topic")
        topic = st.text_input("Enter your study topic:")

        if topic:
            with st.spinner("Generating study materials..."):
                explain_prompt = f"Explain the topic '{topic}' in simple terms."
                summary_prompt = f"Summarize the topic '{topic}' in about 100 words."
                quiz_prompt = (
                    f"Create 5 multiple choice questions with 4 options each (A, B, C, D) about {topic}.\n"
                    f"At the end, provide the correct answers in this format: Answers: 1. B 2. C 3. A 4. D 5. B"
                )

                explanation = model.generate_content(explain_prompt).text
                summary = model.generate_content(summary_prompt).text
                quiz = model.generate_content(quiz_prompt).text

            st.subheader("📖 Explanation")
            st.write(explanation)

            st.subheader("📘 Summary")
            st.write(summary)

            st.subheader("🧠 Quiz")
            st.markdown(quiz)

# ============ FEATURE 2: PROJECT PARTNER MATCHING ============
elif app == "🤝 Find Project Partner":
    st.title("🤝 Find A Project Partner")
    st.write("Find the best fictional teammate based on your interests and personality traits.")

    name = st.text_input("Your Name:")

    personality = st.multiselect(
        "Select your personality traits:",
        ["Introvert", "Extrovert", "Creative", "Analytical", "Leader", "Supporter", "Chill", "Hustler"]
    )

    interests = st.multiselect(
        "Select your interests or skills:",
        ["AI", "Python", "Web Dev", "Graphic Design", "Gaming", "Finance", "Public Speaking", "Photography", "Business"]
    )

    def generate_dummy_profiles(user_interests, user_personality):
        prompt = (
            f"Generate 5 fictional Muslim student profiles who could be great teammates for someone "
            f"with interests: {', '.join(user_interests)} and personality: {', '.join(user_personality)}.\n"
            f"Each profile should include:\n- A Muslim first name\n- 3 interests\n- 2 personality traits\n"
            f"Use this exact format, one profile per line:\n"
            f"Name: <name>; Interests: <interest1>, <interest2>, <interest3>; Personality: <trait1>, <trait2>"
        )

        response = model.generate_content(prompt).text.strip()

        dummy_profiles = []
        for line in response.splitlines():
            try:
                name = line.split("Name:")[1].split(";")[0].strip()
                interests = line.split("Interests:")[1].split(";")[0].split(",")
                personality = line.split("Personality:")[1].split(",")
                dummy_profiles.append({
                    "name": name,
                    "interests": [i.strip() for i in interests],
                    "personality": [p.strip() for p in personality]
                })
            except Exception:
                continue

        return dummy_profiles

    if st.button("🔍 Find My Matches"):
        if not name or not interests or not personality:
            st.error("Please fill in your name, interests, and personality.")
        else:
            with st.spinner("Generating your ideal team..."):
                fake_profiles = generate_dummy_profiles(interests, personality)

                if not fake_profiles:
                    st.error("Gemini couldn't generate any teammate profiles. Please try again.")
                else:
                    profile_text = "\n".join([
                        f"{p['name']} - Interests: {', '.join(p['interests'])}; Personality: {', '.join(p['personality'])}"
                        for p in fake_profiles
                    ])

                    match_prompt = (
                        f"{name} has interests: {', '.join(interests)} and personality: {', '.join(personality)}.\n\n"
                        f"Here are fictional Muslim student profiles:\n{profile_text}\n\n"
                        f"Choose the top 2 most compatible people. Use this exact format:\n"
                        f"Name: <name>\nCompatibility: <number>%\nReason: <short explanation>"
                    )

                    try:
                        result = model.generate_content(match_prompt).text.strip()

                        lines = [line.strip() for line in result.splitlines() if line.strip()]
                        matches = []
                        current = {}

                        for line in lines:
                            if line.lower().startswith("name:"):
                                if current:
                                    matches.append(current)
                                    current = {}
                                current['name'] = line.split(":", 1)[-1].strip()
                            elif line.lower().startswith("compatibility"):
                                raw_score = line.split(":", 1)[-1]
                                digits_only = ''.join(filter(str.isdigit, raw_score))
                                current['score'] = int(digits_only) if digits_only else random.randint(65, 90)
                            elif line.lower().startswith("reason"):
                                current['reason'] = line.split(":", 1)[-1].strip()

                        if current:
                            matches.append(current)

                        matches = matches[:2]

                        if len(matches) >= 1:
                            st.subheader("🏆 Best Match")
                            st.write(f"**{matches[0]['name']}**")
                            st.progress(matches[0]['score'])
                            st.caption(f"🔗 Compatibility: {matches[0]['score']}%")
                            st.write(f"🧠 _Why this match?_ {matches[0]['reason']}")

                            proj_prompt = (
                                f"Suggest a project idea for {name} and {matches[0]['name']} based on shared interests: "
                                f"{', '.join(interests)}. Also assign roles for both."
                            )
                            project = model.generate_content(proj_prompt).text.strip()
                            st.subheader("💡 Project Idea With Best Match")
                            st.write(project)

                        if len(matches) >= 2:
                            st.subheader("🤝 Also Compatible")
                            st.write(f"**{matches[1]['name']}**")
                            st.progress(matches[1]['score'])
                            st.caption(f"🔗 Compatibility: {matches[1]['score']}%")
                            st.write(f"🧠 _Why this match?_ {matches[1]['reason']}")

                    except Exception as e:
                        st.error(f"❌ Gemini error during matching: {e}")
