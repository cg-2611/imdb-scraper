import requests

from bs4 import BeautifulSoup
from enum import Enum

URL = "https://www.imdb.com/chart/"

class Flags(Enum):
    MOVIE = "movie"
    TV_SHOW = "tv-show"
    TOP_RATED = ["top-rated", "top", "toptv"]
    MOST_POPULAR = ["most-popular", "moviemeter", "tvmeter"]


class IMDbScraper:
    def __init__(self, medium: Flags, type: Flags, genre:str) -> None:
        self.medium = medium
        self.type = type
        self.genre = genre

        self.url = self.__get_url()

        self.page = requests.get(self.url)
        self.soup = BeautifulSoup(self.page.text, "html.parser")

        self.genres = [genre for genre in self.__get_genres()]

    def __get_url(self) -> str:
        if self.medium == Flags.MOVIE:
            page_name = self.type.value[1]
        elif  self.medium == Flags.TV_SHOW:
            page_name = self.type.value[2]

        return URL + page_name + "/"

    def __get_genres(self) -> str:
        genre_list_soup = self.soup.find("ul", class_="quicklinks")
        genre_list_items_soup = genre_list_soup.find_all("li", class_="subnav_item_main")

        for genre in genre_list_items_soup:
            yield genre.get_text().strip().lower().replace(" ", "-")
