import requests
import sys

from bs4 import BeautifulSoup


URL = "https://www.imdb.com/"
GENRES_URL = "https://www.imdb.com/feature/genre/"


def format_genre(genre: str) -> str:
    return genre.get_text().strip().lower().replace(" ", "-")

def main() -> None:
    page = requests.get(GENRES_URL)
    soup = BeautifulSoup(page.text, "html.parser")

    movie_genres_soup = soup.find_all("div", class_="article")[5]
    tv_genres_soup = soup.find_all("div", class_="article")[6]

    movie_genres = [format_genre(genre) for genre in movie_genres_soup.find_all("div", class_="table-cell primary")]
    tv_genres = [format_genre(genre) for genre in tv_genres_soup.find_all("div", class_="table-cell primary")]

    print(movie_genres)
    print(tv_genres)


if __name__ == "__main__":
    main()
