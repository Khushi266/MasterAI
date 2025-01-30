import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import neattext.functions as nfx
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
nltk.download('stopwords')
nltk.download('wordnet')
class CourseRecommender:
    def __init__(self, data_path='courses (1).csv'):
        
        self.data = pd.read_csv(data_path)

     
        self.data['combined_text'] = self.data['course_title'] + ' ' + self.data['description']

        
        self.data['clean_description'] = self.data['combined_text'].apply(nfx.remove_stopwords)
        self.data['clean_description'] = self.data['clean_description'].apply(nfx.remove_special_characters)

      
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()


        self.data['cleaned_description'] = self.data['clean_description'].apply(self.clean_text)
        self.data = self.data.drop(['combined_text', 'clean_description'], axis=1)

  
        self.tfidf = TfidfVectorizer(max_features=5000)  
        self.tfidf_matrix = self.tfidf.fit_transform(self.data['cleaned_description'])

    def clean_text(self, text):
        """Clean and preprocess the input text."""
        text = re.sub(r'[^\w\s]', '', text) 
        text = text.lower() 
        text = ' '.join([self.lemmatizer.lemmatize(word) for word in text.split() if word not in self.stop_words])  # Remove stopwords and lemmatize
        return text

    def recommend_courses(self, user_input, top_n=10):
        """Recommend courses based on user input."""
        cleaned_input = self.clean_text(user_input)
        input_vector = self.tfidf.transform([cleaned_input])
        similarities = cosine_similarity(input_vector, self.tfidf_matrix).flatten()
        top_indices = similarities.argsort()[-top_n:][::-1]
        recommendations = self.data.iloc[top_indices].copy()
        recommendations['similarity_score'] = similarities[top_indices]
        recommendations['weighted_score'] = recommendations['similarity_score'] * recommendations['num_subscribers']

  
        recommendations = recommendations.sort_values(by='weighted_score', ascending=False)

        return recommendations.head(top_n)

    def run_streamlit_app(self):
        """Run the Streamlit app."""
        import streamlit as st

    

   
        user_input = st.text_input('Enter your preferences or course details you are looking for:')

        if user_input:
          
            recommendations = self.recommend_courses(user_input)

            st.write('Recommended Courses for you:')

            table_data = []
            for idx, row in recommendations.iterrows():
                course_title = row['course_title']
                course_url = row.get('url')
                course_link = f'<a href="{course_url}" target="_blank">{course_title}</a>'  # Create a clickable link
                table_data.append({
                    'Course Title': course_link,
                    'Number of Subscribers': row['num_subscribers'],
                    'Difficulty Level': row['difficulty'],
                    'Platform': row['organization'],
                    'Similarity Score': f"{row['similarity_score']:.2f}",
                })
            
          
            st.markdown(
                """
                <style>
                table {
                    width: 100%;
                }
                th, td {
                    text-align: left;
                    padding: 8px;
                }
                th {
                    background-color: #f2f2f2;
                }
                </style>
                """, unsafe_allow_html=True
            )

           
            df_table = pd.DataFrame(table_data)


            st.markdown(df_table.to_html(escape=False, index=False), unsafe_allow_html=True)
      


if __name__ == "__main__":
    recommender = CourseRecommender()
    recommender.run_streamlit_app()
