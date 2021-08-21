from bs4.element import PageElement
import requests

from bs4 import BeautifulSoup
from content import Movie
from enum import Enum


URL = "https://www.imdb.com/search/title/"


class Types(Enum):
    MOVIE = "movie"
    TV_SHOW = "tv-show"
    TOP_RATED = "top-rated"
    MOST_POPULAR = "most-popular"


class IMDbScraper:
    def __init__(self, content_type: Types, ranking_type: Types, genre:str, votes:int, limit: int) -> None:
        self.content_type = content_type
        self.ranking_type = ranking_type
        self.genre = genre
        self.votes = votes if votes > 1 else 25000
        self.limit = limit
        self.url = self.__get_url()
        self.genres = [genre for genre in self.__get_genres()]

        print(self.genres)

    def __get_url(self) -> str:
        if self.content_type == Types.MOVIE:
            page_name = self.ranking_type.value[1]
        elif self.content_type == Types.TV_SHOW:
            page_name = self.ranking_type.value[2]

        return URL + page_name + "/"

    def __get_genres(self) -> str:
        genre_table_soup = self.__get_genres_list()
        genre_list_soup = genre_table_soup.find_all("div", class_="table-cell primary")

        for genre in genre_list_soup:
            yield genre.find("a").get_text().strip().lower().replace(" ", "-")

    def __get_genres_list(self) -> str:
        genre_page = requests.get("https://www.imdb.com/feature/genre/")
        genre_page_soup = BeautifulSoup(genre_page.text, "html.parser")

        genre_table_soup = genre_page_soup.find_all("div", class_="ab_links")

        if self.content_type == Types.MOVIE:
            return genre_table_soup[0]
        elif self.content_type == Types.TV_SHOW:
            return genre_table_soup[1]

    def __get_movie_information(self, movie_soup: PageElement) -> tuple:
        name = movie_soup.find("a")
        name_value = name.get_text().strip() if name is not None else None

        year = movie_soup.find("span", class_="lister-item-year")
        year_value = year.get_text().strip() if year is not None else None

        rank = movie_soup.find("span", class_="lister-item-index")
        rank_value = int(rank.get_text().replace(".", "").replace(",", "").strip()) if rank is not None else None

        rating = movie_soup.find("span", class_="imdb-rating").find("strong")
        rating_value = float(rating.get_text().strip()) if rating is not None else None

        duration = movie_soup.find("span", class_="runtime")
        duration_value = int(duration.get_text().strip().replace(" min", "")) if duration is not None else None

        certificate = movie_soup.find("span", class_="certificate")
        certificate_value = certificate.get_text().strip() if certificate is not None else None

        votes_and_gross = movie_soup.find("p", class_="sort-num_votes-visible").find_all("span", attrs={'name':'nv'})

        votes_value = int(votes_and_gross[0].get("data-value"))

        gross_value = None
        if len(votes_and_gross) == 2:
            gross_value = int(votes_and_gross[1].get("data-value").replace(",", ""))

        return name_value, year_value, rank_value, rating_value, duration_value, certificate_value, votes_value, gross_value

    def get_movies(self) -> list:
        movies = []
        i = 1

        url = URL + f"?genres={self.genre}&sort=user_rating,desc&title_type=feature&start=%d&num_votes={self.votes},"

        page_soup = BeautifulSoup(requests.get(url % i).text, "html.parser")
        total_string = page_soup.find("div", class_="desc").find("span").get_text().replace(",", "")
        total = [int(x) for x in total_string.split() if x.isdigit()][0]

        if self.limit is None:
            total_rankings = total
        else:
            total_rankings = total if total < self.limit else self.limit

        print(f"Searching through {total_rankings} movies...")

        while  True:
            rankings_page = requests.get(url % i)
            rankings_list_soup = BeautifulSoup(rankings_page.text, "html.parser")
            rankings_soup = rankings_list_soup.find_all("div", class_="lister-item-content")

            for ranking in rankings_soup:
                ranking_information = self.__get_movie_information(ranking)
                movie = Movie(*ranking_information)

                # if movie.duration > 150:
                movies.append(movie)

            i += 50
            if i > total_rankings:
                break

        print(f"Found {len(movies)} matches:")
        return movies
