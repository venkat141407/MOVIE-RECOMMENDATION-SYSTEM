import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity

# Load datasets
movies = pd.read_csv("movies.csv")
ratings = pd.read_csv("ratings.csv")

# Get top 5000 most-rated movies
top_movies = (
    ratings.groupby("movieId")
    .size()
    .sort_values(ascending=False)
    .head(1000)
    .index
)

movies = movies[movies["movieId"].isin(top_movies)]
ratings = ratings[ratings["movieId"].isin(top_movies)]

# Merge
data = movies.merge(ratings, on="movieId")

# User-Movie Matrix
movie_matrix = data.pivot_table(
    index="title",
    columns="userId",
    values="rating",
    fill_value=0
)

print("Movies used:", len(movie_matrix))

# Cosine Similarity
similarity = cosine_similarity(movie_matrix)

# Save
movie_titles = pd.DataFrame(movie_matrix.index, columns=["title"])

with open("movies.pkl", "wb") as f:
    pickle.dump(movie_titles, f)

with open("similarity.pkl", "wb") as f:
    pickle.dump(similarity, f)

print("✅ Model trained successfully!")
print("Movies:", len(movie_titles))
