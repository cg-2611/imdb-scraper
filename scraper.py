import requests

from enum import Enum

from bs4 import BeautifulSoup
from bs4 import PageElement

from content import Movie
from content import Show


URL = "https://www.imdb.com/search/title/"


class Types(Enum):
    MOVIE = ["movie", "feature"]
    TV_SHOW = ["tv-show", "tv_series,tv_miniseries"]
    TOP_RATED = ["top-rated"]
    MOST_POPULAR = ["most-popular"]


class IMDbScraper:
    def __init__(self, content_type: Types, ranking_type: Types, genre:str, votes:int, limit: int) -> None:
        self.content_type = content_type
        self.ranking_type = ranking_type
        self.genre = genre

        if self.content_type == Types.MOVIE:
            self.votes = votes if votes > 1 else 25000
        elif self.content_type == Types.TV_SHOW:
            self.votes = votes if votes > 1 else 5000

        self.limit = limit if limit > 1 else None
        self.genres = [genre for genre in self.__get_genres()]

    def __get_url(self) -> str:
        if self.ranking_type == Types.TOP_RATED:
            return URL + f"?genres={self.genre}&sort=user_rating,desc&title_type={self.content_type.value[1]}&start=%d&num_votes={self.votes},"
        elif self.ranking_type == Types.MOST_POPULAR:
            return URL + f"?genres={self.genre}&title_type={self.content_type.value[1]}&start=%d&num_votes={self.votes},"

    def __get_genres_list(self) -> str:
        genre_page = requests.get("https://www.imdb.com/feature/genre/")
        genre_page_soup = BeautifulSoup(genre_page.text, "html.parser")

        genre_table_soup = genre_page_soup.find_all("div", class_="ab_links")

        if self.content_type == Types.MOVIE:
            return genre_table_soup[0]
        elif self.content_type == Types.TV_SHOW:
            return genre_table_soup[1]

    def __get_genres(self) -> str:
        genre_table_soup = self.__get_genres_list()
        genre_list_soup = genre_table_soup.find_all("div", class_="table-cell primary")

        for genre in genre_list_soup:
            yield genre.find("a").get_text().strip().lower().replace(" ", "-")

    def __get_total_results(self, url: str, start: int) -> int:
        page_soup = BeautifulSoup(requests.get(url % start).text, "html.parser")
        total_string = page_soup.find("div", class_="desc").find("span").get_text().replace(",", "")
        total = int("".join(filter(str.isdigit, total_string[total_string.find("of "):])))

        if self.limit is None:
            return total
        else:
            return total if total < self.limit else self.limit

    def __get_movie_information(self, movie_soup: PageElement) -> tuple:
        name = movie_soup.find("a")
        name_value = name.get_text().strip() if name is not None else None

        year = movie_soup.find("span", class_="lister-item-year")
        year_value = int("".join(filter(str.isdigit, year.get_text().strip()))) if year is not None else None

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

    def __get_tv_show_information(self, show_soup) -> tuple:
        name = show_soup.find("a")
        name_value = name.get_text().strip() if name is not None else None

        year = show_soup.find("span", class_="lister-item-year").get_text().strip()

        start = "".join(filter(str.isdigit, year[:year.find("–")]))
        end = "".join(filter(str.isdigit, year[year.find("–"):]))
        start_value = int(start) if (start) and (start is not None) else None
        end_value = int(end) if (end) and (end is not None) else None
        year_value = (start_value, end_value)

        discontinued_value = True if (end) or (year.find("–") == -1) else False

        rank = show_soup.find("span", class_="lister-item-index")
        rank_value = int(rank.get_text().replace(".", "").replace(",", "").strip()) if rank is not None else None

        rating = show_soup.find("span", class_="imdb-rating").find("strong")
        rating_value = float(rating.get_text().strip()) if rating is not None else None

        certificate = show_soup.find("span", class_="certificate")
        certificate_value = certificate.get_text().strip() if certificate is not None else None

        votes_and_gross = show_soup.find("p", class_="sort-num_votes-visible").find_all("span", attrs={'name':'nv'})
        votes_value = int(votes_and_gross[0].get("data-value"))


        return name_value, year_value, discontinued_value, rank_value, rating_value, certificate_value, votes_value

    def get_movies(self) -> list:
        movies = []
        i = 1

        url = self.__get_url()
        total_rankings = self.__get_total_results(url, 1)

        print(f"Searching through {total_rankings} movies...")

        search_complete = False
        while not search_complete:
            rankings_page = requests.get(url % i)
            rankings_list_soup = BeautifulSoup(rankings_page.text, "html.parser")
            rankings_soup = rankings_list_soup.find_all("div", class_="lister-item-content")

            for ranking in rankings_soup:
                i += 1

                ranking_information = self.__get_movie_information(ranking)
                movie = Movie(*ranking_information)
                movies.append(movie)

                if i > total_rankings:
                    search_complete = True
                    break

        print(f"Found {len(movies)} matches:")
        return movies

    def get_tv_shows(self) -> list:
        shows = []
        i = 1

        url = self.__get_url()
        total_rankings = self.__get_total_results(url, 1)

        print(f"Searching through {total_rankings} shows...")

        search_complete = False
        while not search_complete:
            rankings_page = requests.get(url % i)
            rankings_list_soup = BeautifulSoup(rankings_page.text, "html.parser")
            rankings_soup = rankings_list_soup.find_all("div", class_="lister-item-content")

            for ranking in rankings_soup:
                i += 1

                ranking_information = self.__get_tv_show_information(ranking)
                show = Show(*ranking_information)
                shows.append(show)

                if i > total_rankings:
                    search_complete = True
                    break

        print(f"Found {len(shows)} matches:")
        return shows
