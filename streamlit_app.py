import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Page Settings
st.set_page_config(
    page_title="Movie Recommendation Engine",
    page_icon="🎬",
    layout="wide"
)

# Load Data
ratings = pd.read_csv("data/ratings.csv")
movies = pd.read_csv("data/movies.csv")

ratings.columns = ratings.columns.str.strip()
movies.columns = movies.columns.str.strip()

# Create User-Movie Matrix
user_movie_matrix = ratings.pivot_table(
    index="user_id",
    columns="movie_id",
    values="rating"
).fillna(0)

# Similarity Matrix
similarity_matrix = cosine_similarity(user_movie_matrix)

similarity_df = pd.DataFrame(
    similarity_matrix,
    index=user_movie_matrix.index,
    columns=user_movie_matrix.index
)

# Recommendation Function
def recommend_movies(user_id, top_n=5):

    if user_id not in user_movie_matrix.index:
        return pd.DataFrame()

    similar_users = similarity_df[user_id].sort_values(
        ascending=False
    )

    similar_users = similar_users.drop(user_id)

    recommendation_scores = {}

    user_movies = user_movie_matrix.loc[user_id]

    top_users = similar_users.head(3)

    for similar_user, similarity_score in top_users.items():

        similar_user_movies = user_movie_matrix.loc[similar_user]

        for movie in user_movie_matrix.columns:

            if (
                user_movies[movie] == 0
                and similar_user_movies[movie] > 0
            ):

                recommendation_scores[movie] = (
                    recommendation_scores.get(movie, 0)
                    + similar_user_movies[movie]
                    * similarity_score
                )

    sorted_movies = sorted(
        recommendation_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    results = []

    for movie_id, score in sorted_movies[:top_n]:

        movie_row = movies[movies["movie_id"] == movie_id]

        if not movie_row.empty:
            movie_name = movie_row["title"].values[0]
        else:
            movie_name = f"Movie {movie_id}"

        results.append({
            "Movie": movie_name,
            "Score": round(score, 2)
        })

    return pd.DataFrame(results)

# Sidebar
with st.sidebar:
    st.header("📊 Project Information")
    st.write("Recommendation System using Collaborative Filtering")

    st.metric("Total Users", len(user_movie_matrix))
    st.metric("Total Movies", len(movies))

# Main UI
st.title("🎬 Movie Recommendation Engine")

st.markdown(
    "Get personalized movie recommendations based on similar users."
)

# Search Movies
st.subheader("🔍 Search Movies")

movie_search = st.text_input("Enter Movie Name")

if movie_search:

    filtered_movies = movies[
        movies["title"].str.contains(
            movie_search,
            case=False,
            na=False
        )
    ]

    if not filtered_movies.empty:
        st.dataframe(filtered_movies[["movie_id", "title"]])
    else:
        st.warning("No movie found!")

# Rating Distribution Chart
st.subheader("📊 Ratings Distribution")

st.bar_chart(
    ratings["rating"].value_counts().sort_index()
)

# User Input
user_id = st.number_input(
    "Enter User ID",
    min_value=1,
    step=1
)

# Show User Rated Movies
if user_id in user_movie_matrix.index:

    st.subheader("🎞 Movies Rated By User")

    user_ratings = ratings[
        ratings["user_id"] == user_id
    ]

    for _, row in user_ratings.iterrows():

        movie_name = movies[
            movies["movie_id"] == row["movie_id"]
        ]["title"].values[0]

        st.write(
            f"⭐ {movie_name} | Rating: {row['rating']}"
        )

# Recommendation Button
if st.button("🔍 Recommend Movies"):

    recommendations = recommend_movies(user_id)

    if not recommendations.empty:

        st.success("Top Recommendations")

        # Score Chart
        st.subheader("📈 Recommendation Score Chart")

        chart_df = recommendations.set_index("Movie")

        st.bar_chart(chart_df["Score"])

        # Recommendation Cards
        for _, row in recommendations.iterrows():

            st.markdown("---")

            st.subheader(f"🎥 {row['Movie']}")

            st.write(
                f"⭐ Recommendation Score: {row['Score']}"
            )

        # Download CSV
        csv = recommendations.to_csv(index=False)

        st.download_button(
            label="📥 Download Recommendations",
            data=csv,
            file_name="recommendations.csv",
            mime="text/csv"
        )

    else:
        st.warning(
            "No recommendations found for this user."
        )
