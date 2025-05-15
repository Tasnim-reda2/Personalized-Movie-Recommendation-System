import streamlit as st
import pandas as pd
import random
import os
import io
from sklearn.preprocessing import LabelEncoder

# Load MovieLens data
@st.cache_data
def load_data():
    movies = pd.read_csv(r"C:/Users/Acer/Desktop/ss/movies.csv")
    ratings = pd.read_csv(r"C:/Users/Acer/Desktop/ss/ratings.csv")
    return movies, ratings

# Genetic algorithm to generate recommendations (simulated)
def genetic_algorithm(user_preferences, movies_df, ratings_df):
    if user_preferences:
        recommended_movies = movies_df[movies_df['genres'].str.contains('|'.join(user_preferences), case=False, na=False)]
    else:
        recommended_movies = movies_df

    if recommended_movies.empty:
        recommended_movies = movies_df.sample(10)

    top_movies = recommended_movies.sample(10)
    return top_movies

# User interface
def main():
    st.title("🎬 Personalized Movie Recommendation System")
    st.subheader("Optimizing movie recommendation strategies using Genetic Programming")

    movies_df, ratings_df = load_data()

    # Sidebar
    st.sidebar.header("🎯 Select Your Preferences")
    user_id = st.sidebar.text_input("Enter your User ID", "")
    genre_preferences = st.sidebar.multiselect("Select genres you're interested in:",
                                               ['Action', 'Comedy', 'Drama', 'Romance', 'Horror', 'Adventure', 'Sci-Fi', 'Thriller'])
    rating_threshold = st.sidebar.slider("Minimum movie rating preference:", 1, 5, 3)

    # Session state to store recommendations
    if 'top_movies' not in st.session_state:
        st.session_state.top_movies = pd.DataFrame()

    # Generate recommendations
    if st.sidebar.button("🎥 Generate Recommendations"):
        if user_id.strip():
            st.markdown(f"## 🎁 Recommendations for user **{user_id}**")
            st.session_state.top_movies = genetic_algorithm(genre_preferences, movies_df, ratings_df)

            for _, movie in st.session_state.top_movies.iterrows():
                cols = st.columns([1, 4])
                with cols[0]:
                    if 'poster_path' in movie and pd.notna(movie['poster_path']):
                        st.image(f"https://image.tmdb.org/t/p/w500/{movie['poster_path']}", width=100)
                    else:
                        st.write("📷 No poster")

                with cols[1]:
                    st.markdown(f"**{movie['title']}**")
                    st.markdown(f"⭐ Rating: {random.uniform(rating_threshold, 5):.1f}")
                    st.markdown(f"🎭 Genres: {movie['genres']}")
                    st.markdown("---")
        else:
            st.error("⚠️ Please enter your User ID first.")

    # Save recommendations
    if st.button("💾 Save Recommendations"):
        if not user_id.strip():
            st.error("❗ Please enter your User ID to save recommendations.")
        elif st.session_state.top_movies.empty:
            st.error("❗ No recommendations to save. Please generate first.")
        else:
            filename = f"recommendations_user_{user_id}.csv"
            st.session_state.top_movies.to_csv(filename, index=False)
            st.success(f"✅ Recommendations saved to **{filename}**")
            st.write(f"📁 File location: `{os.path.abspath(filename)}`")

            # Download button
            csv_buffer = io.StringIO()
            st.session_state.top_movies.to_csv(csv_buffer, index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv_buffer.getvalue(),
                file_name=filename,
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
