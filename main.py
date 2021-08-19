import requests
import sys

from bs4 import BeautifulSoup


URL = "https://www.imdb.com/chart/"


def get_args() -> tuple:
    charts_flag = True if "-c" in sys.argv else False
    popular_flag = True if "-p" in sys.argv else False

    if charts_flag and popular_flag:
        raise ValueError("cannot set both charts and popular flags, must use one or the other")
    elif not charts_flag and not popular_flag:
        raise ValueError("neither charts nor popular flag set, exactly one flag must be set")

    movie_flag = True if "-m" in sys.argv else False
    tv_flag = True if "-t" in sys.argv else False

    if movie_flag and tv_flag:
        raise ValueError("cannot set both movie and tv flags, must use one or the other")
    elif not movie_flag and not tv_flag:
        raise ValueError("neither movie nor tv flag set, exactly one flag must be set")

    return charts_flag, popular_flag, movie_flag, tv_flag

def generate_url(flags: tuple) -> str:
    charts_flag, popular_flag, movie_flag, tv_flag = flags
    if charts_flag:
        if movie_flag:
            return URL + "top/"
        elif tv_flag:
            return URL + "toptv/"
    elif popular_flag:
        if movie_flag:
            return URL + "moviemeter/"
        elif tv_flag:
            return URL + "tvmeter/"

def get_genres(soup: BeautifulSoup) -> str:
    genre_list_soup = soup.find("ul", class_="quicklinks")
    genre_list_items_soup = genre_list_soup.find_all("li", class_="subnav_item_main")

    for genre in genre_list_items_soup:
        yield genre.get_text().strip().lower().replace(" ", "-")

def main() -> None:
    flags = get_args()

    generated_url = generate_url(flags)

    page = requests.get(generated_url)
    soup = BeautifulSoup(page.text, "html.parser")

    genres = [genre for genre in get_genres(soup)]

    print(genres)


if __name__ == "__main__":
    main()
