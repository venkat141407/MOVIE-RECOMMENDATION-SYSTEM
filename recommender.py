import pickle
import requests
import config
import re

# Load trained data
movies = pickle.load(open("movies.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))


def clean_title(title):
    """
    Convert MovieLens title into a format that OMDb understands.
    """

    title = re.sub(r'^\d+\s*', '', title)
    title = re.sub(r'\(\d{4}\)', '', title).strip()

    if title.endswith(", The"):
        title = "The " + title[:-5]

    elif title.endswith(", A"):
        title = "A " + title[:-3]

    elif title.endswith(", An"):
        title = "An " + title[:-4]

    return title.strip()


def get_movie_details(title):

    search_title = clean_title(title)

    url = f"https://www.omdbapi.com/?t={search_title}&apikey={config.OMDB_API_KEY}"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if data.get("Response") == "True":
            return {
                "title": data.get("Title"),
                "poster": data.get("Poster"),
                "rating": data.get("imdbRating"),
                "genre": data.get("Genre"),
                "year": data.get("Year"),
                "plot": data.get("Plot")
            }

    except Exception as e:
        print("OMDb Error:", e)

    return {
        "title": search_title,
        "poster": "https://via.placeholder.com/300x450?text=No+Poster",
        "rating": "N/A",
        "genre": "N/A",
        "year": "",
        "plot": "Movie details not found."
    }


def recommend(movie_name):

    movie = movies[
        movies["title"].str.lower() == movie_name.lower()
    ]

    if movie.empty:
        return []

    movie_index = movie.index[0]

    distances = list(enumerate(similarity[movie_index]))

    movie_list = sorted(
        distances,
        key=lambda x: x[1],
        reverse=True
    )[1:11]

    recommendations = []

    for item in movie_list:

        title = movies.iloc[item[0]].title

        recommendations.append(
            get_movie_details(title)
        )

    return recommendations


# ===========================
# AUTOCOMPLETE FUNCTION
# ===========================

def autocomplete(query):

    if not query:
        return []

    query = query.lower()

    matches = movies[
        movies["title"].str.lower().str.contains(query, na=False)
    ]["title"].drop_duplicates().head(10)

    return matches.tolist()