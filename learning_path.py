import streamlit as st
import os
from ai21 import AI21Client
from ai21.models.chat import ChatMessage

class LearningPlanApp:
    def __init__(self):
      
        os.environ["AI21_API_KEY"] = "AdWkhSmvVEMbaTSc7MqfMG5rBveZPSoN"
        self.client = AI21Client(api_key=os.getenv("AI21_API_KEY"))

    
        self.TARGET_ROLE_SKILLS = {
            "Data Scientist": ["Python", "Data Analysis", "Machine Learning", "SQL", "Statistics", "Data Visualization"],
            "Software Engineer": ["Python", "Java", "C++", "Data Structures", "Algorithms", "Git"],
            "Product Manager": ["Product Management", "Agile", "Scrum", "Market Research", "Data Analysis", "Communication"]
        }

    def calculate_skill_gap(self, user_skills, target_skills):
        """Calculate the skill gap and percentage match."""
        user_skills_set = set(user_skills)
        target_skills_set = set(target_skills)
        
        matched_skills = user_skills_set.intersection(target_skills_set)
        
 
        percentage_match = (len(matched_skills) / len(target_skills_set)) * 100
        
        skills_to_learn = target_skills_set - user_skills_set
        
        return percentage_match, skills_to_learn

    def handle_conversation(self, messages, model="jamba-instruct-preview", n=1, max_tokens=1024, temperature=0.7, top_p=1, stop=[]):
        """Handle conversation with AI21."""
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            n=n,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=stop,
        )
        
        if response.choices:
            return response.choices[0].message.content
        return None

    def generate_learning_plan(self, goal, skills, learning_style, time_commitment):
        """Generate a personalized learning plan."""
        if goal in self.TARGET_ROLE_SKILLS:
            target_skills = self.TARGET_ROLE_SKILLS[goal]
            percentage_match, skills_to_learn = self.calculate_skill_gap(skills, target_skills)
            
            st.write(f"### Skill Gap Analysis for {goal}")
            st.write(f"**Percentage Match with Target Role:** {percentage_match:.2f}%")
            st.write("**Skills You Need to Learn:**")
            for skill in skills_to_learn:
                st.write(f"- {skill}")
            
            st.write("### Your Personalized Learning Path")
            
       
            messages = [
                ChatMessage(
                    content=f"""Recommend a personalized learning path based on following parameters:
                    goal : {goal},
                    current skills : {skills},
                    skills to learn : {list(skills_to_learn)},
                    learning style : {learning_style},
                    time period : {time_commitment} per week
                    """, role="assistant"
                )
            ]
            
            learning_path = self.handle_conversation(messages, model="jamba-instruct-preview", n=1, max_tokens=500, temperature=0.7, top_p=1, stop=[])
            st.write(f"AI: {learning_path}")
            
            st.write("### Progress Tracker")
            st.progress(percentage_match / 100)
        else:
            st.write("Please enter a valid career goal (e.g., Data Scientist, Software Engineer, Product Manager).")

    def run(self):
        """Run the Streamlit app."""
        st.title("Personalized Learning Plan")


        goal = st.selectbox("Select your academic or career goal:", list(self.TARGET_ROLE_SKILLS.keys()))
        skills = st.multiselect("Select your current skills:", list(set(sum(self.TARGET_ROLE_SKILLS.values(), []))))
        learning_style = st.selectbox("Preferred learning style:", ["Video-based", "Hands-on Projects", "Reading"])
        time_commitment = st.selectbox("Time commitment per week:", ["1-5 hours", "5-10 hours", "10+ hours"])

      
        if st.button("Generate Learning Plan"):
            self.generate_learning_plan(goal, skills, learning_style, time_commitment)

  
        feedback = st.radio("Was this course helpful?", ["Yes", "No"])
        if feedback == "No":
            st.write("We'll adjust your learning path.")


if __name__ == "__main__":
    app = LearningPlanApp()
    app.run()