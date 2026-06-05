import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Load datasets
ratings = pd.read_csv("data/ratings.csv")
movies = pd.read_csv("data/movies.csv")

# Create User-Movie Matrix
user_movie_matrix = ratings.pivot_table(
    index='user_id',
    columns='movie_id',
    values='rating'
).fillna(0)

# Calculate Similarity Matrix
similarity_matrix = cosine_similarity(user_movie_matrix)

similarity_df = pd.DataFrame(
    similarity_matrix,
    index=user_movie_matrix.index,
    columns=user_movie_matrix.index
)

# Recommendation Function
def recommend_movies(user_id, top_n=5):

    if user_id not in user_movie_matrix.index:
        return []

    similar_users = similarity_df[user_id].sort_values(
        ascending=False
    )

    similar_users = similar_users.drop(user_id)

    recommendation_scores = {}

    user_movies = user_movie_matrix.loc[user_id]

    # Take top 3 similar users
    top_users = similar_users.head(3)

    for similar_user, similarity_score in top_users.items():

        similar_user_movies = user_movie_matrix.loc[similar_user]

        for movie in user_movie_matrix.columns:

            if user_movies[movie] == 0 and similar_user_movies[movie] > 0:

                if movie not in recommendation_scores:
                    recommendation_scores[movie] = 0

                recommendation_scores[movie] += (
                    similar_user_movies[movie]
                    * similarity_score
                )

    sorted_movies = sorted(
        recommendation_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    recommendations = []

    for movie_id, score in sorted_movies[:top_n]:

        movie_name = movies[
            movies["movie_id"] == movie_id
        ]["title"].values[0]

        recommendations.append(
            {
                "Movie": movie_name,
                "Score": round(score, 2)
            }
        )

    return recommendations


# User Input
user_id = int(input("Enter User ID: "))

recommendations = recommend_movies(user_id)

print("\nTop Recommendations\n")

for rec in recommendations:
    print(
        f"{rec['Movie']} "
        f"(Score: {rec['Score']})"
    )
