import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity

# Load datasets
movies = pd.read_csv("movies.csv")
ratings = pd.read_csv("ratings.csv")

# Merge movies with ratings
data = movies.merge(ratings, on="movieId")

# Create user-movie matrix
movie_matrix = data.pivot_table(
    index="title",
    columns="userId",
    values="rating"
)

# Fill missing values with 0
movie_matrix = movie_matrix.fillna(0)

# Calculate cosine similarity
similarity = cosine_similarity(movie_matrix)

# Save movie titles
movie_titles = pd.DataFrame(movie_matrix.index, columns=["title"])

# Save files
pickle.dump(movie_titles, open("movies.pkl", "wb"))
pickle.dump(similarity, open("similarity.pkl", "wb"))

print("✅ Model trained successfully!")
print("Files created:")
print(" - movies.pkl")
print(" - similarity.pkl")