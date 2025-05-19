import streamlit as st
import pandas as pd
import random
import os
import io

# Load MovieLens data
@st.cache_data
def load_data():
    movies = pd.read_csv("C:/Users/Acer/Desktop/ss/movies.csv")
    ratings = pd.read_csv("C:/Users/Acer/Desktop/ss/ratings.csv")
    return movies, ratings

# Extract top genres based on user's highly-rated movies
def get_user_preferences(user_id, movies_df, ratings_df, min_rating=4):
    try:
        user_id = int(user_id)
    except:
        return []

    user_rated = ratings_df[(ratings_df['userId'] == user_id) & (ratings_df['rating'] >= min_rating)]
    merged = pd.merge(user_rated, movies_df, on='movieId')

    genre_counts = {}
    for genres in merged['genres']:
        for genre in genres.split('|'):
            genre_counts[genre] = genre_counts.get(genre, 0) + 1

    sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
    top_genres = [genre for genre, _ in sorted_genres[:3]]  # Top 3 preferred genres

    return top_genres

# Simplified Genetic Algorithm to simulate recommendation optimization
def genetic_algorithm(user_id, movies_df, ratings_df):
    preferences = get_user_preferences(user_id, movies_df, ratings_df)

    if preferences:
        population = movies_df[movies_df['genres'].str.contains('|'.join(preferences), case=False, na=False)]
    else:
        population = movies_df.copy()

    if population.empty:
        population = movies_df.sample(10)

    # Simulate "evolution" of recommendation strategies
    for _ in range(3):  # Number of generations
        population['fitness'] = population['genres'].apply(lambda g: sum(g.count(p) for p in preferences))
        population = population.sort_values(by='fitness', ascending=False).head(50)
        mutated = population.sample(10).copy()
        mutated['title'] = mutated['title'].sample(frac=1).values  # Simulate mutation
        population = pd.concat([population, mutated], ignore_index=True)

    final_selection = population.drop_duplicates('movieId').sample(min(10, len(population)))
    return final_selection

# Streamlit user interface
def main():
    st.title("🎬 Personalized Movie Recommendation System")
    st.subheader("Optimizing movie recommendation strategies using Genetic Programming")

    movies_df, ratings_df = load_data()

    st.sidebar.header("🎯 User Configuration")
    user_id = st.sidebar.text_input("Enter your User ID", "")
    rating_threshold = st.sidebar.slider("Minimum rating to consider a movie favorite:", 1, 5, 4)

    if 'top_movies' not in st.session_state:
        st.session_state.top_movies = pd.DataFrame()

    if st.sidebar.button("🎥 Generate Recommendations"):
        if user_id.strip():
            st.markdown(f"## 🎁 Recommendations for user **{user_id}**")
            st.session_state.top_movies = genetic_algorithm(user_id, movies_df, ratings_df)

            for _, movie in st.session_state.top_movies.iterrows():
                cols = st.columns([1, 4])
                with cols[0]:
                    st.write("📷 No poster")
                with cols[1]:
                    st.markdown(f"**{movie['title']}**")
                    st.markdown(f"🎭 Genres: {movie['genres']}")
                    st.markdown("---")
        else:
            st.error("⚠️ Please enter your User ID first.")

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
