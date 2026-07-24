import os
import pickle
import requests
import config
import re

# ==========================
# DOWNLOAD similarity.pkl IF MISSING
# ==========================

FILE_PATH = "similarity.pkl"

if not os.path.exists(FILE_PATH):
    print("Downloading similarity.pkl from Google Drive...")

    FILE_ID = "1ixmBPlgjg0WESPfQle4Kvj3t-23Ix-_a"

    session = requests.Session()

    response = session.get(
        "https://drive.google.com/uc?export=download",
        params={"id": FILE_ID},
        stream=True
    )

    token = None
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            token = value
            break

    if token:
        response = session.get(
            "https://drive.google.com/uc?export=download",
            params={"id": FILE_ID, "confirm": token},
            stream=True
        )

    with open(FILE_PATH, "wb") as f:
        for chunk in response.iter_content(32768):
            if chunk:
                f.write(chunk)

    print("Download completed.")

# ==========================
# LOAD TRAINED DATA
# ==========================

movies = pickle.load(open("movies.pkl", "rb"))
similarity = pickle.load(open(FILE_PATH, "rb"))


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
