import requests
import threading

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
    def __init__(self, content_type: Types, ranking_type: Types, genre:str, votes:int, limit: int, filter: str) -> None:
        self.content_type = content_type
        self.ranking_type = ranking_type
        self.genre = genre

        if self.content_type == Types.MOVIE:
            self.votes = votes if votes > 1 else 25000
        elif self.content_type == Types.TV_SHOW:
            self.votes = votes if votes > 1 else 5000

        self.limit = limit if limit > 1 else None
        self.genres = [genre for genre in self.__get_genres()]

        self.filter = filter

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

    def __get_movie_filter_options(self) -> tuple:
        year_filter, rating_filter, duration_filter = None, None, None

        if self.filter is not None:
            filter_options = self.filter.split()

            for option in filter_options:
                if option.startswith("y"):
                    year_filter = [option[1], int(option[2:])]
                    continue

                if option.startswith("r"):
                    rating_filter = [option[1], float(option[2:])]
                    continue

                if option.startswith("d"):
                    duration_filter = [option[1], int(option[2:])]
                    continue

        return (year_filter, rating_filter, duration_filter)

    def __get_tv_show_filter_options(self) -> tuple:
        year_filter, rating_filter, discontinued_filter = None, None, None

        if self.filter is not None:
            filter_options = self.filter.split()

            for option in filter_options:
                if option.startswith("y"):
                    year_filter = [option[1], int(option[2:])]
                    continue

                if option.startswith("r"):
                    rating_filter = [option[1], float(option[2:])]
                    continue

                if option.startswith("d"):
                    value_index = option.find("=")
                    value = option[value_index + 1:]
                    discontinued_filter = False if value == "False" else True
                    continue

        return (year_filter, rating_filter, discontinued_filter)

    def __get_movie_information(self, movie_soup: PageElement) -> tuple:
        name = movie_soup.find("a")
        name_value = name.get_text().strip() if name is not None else None

        year = movie_soup.find("span", class_="lister-item-year")
        year_value = int("".join(filter(str.isdigit, year.get_text().strip()))) if year is not None else None

        rank = movie_soup.find("span", class_="lister-item-index")
        rank_value = int(rank.get_text().replace(".", "").replace(",", "").strip()) if rank is not None else None

        rating = movie_soup.find("div", class_="ratings-imdb-rating").find("strong")
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

        rating = show_soup.find("div", class_="ratings-imdb-rating").find("strong")
        rating_value = float(rating.get_text().strip()) if rating is not None else None

        certificate = show_soup.find("span", class_="certificate")
        certificate_value = certificate.get_text().strip() if certificate is not None else None

        votes_and_gross = show_soup.find("p", class_="sort-num_votes-visible").find_all("span", attrs={'name':'nv'})
        votes_value = int(votes_and_gross[0].get("data-value"))

        return name_value, year_value, discontinued_value, rank_value, rating_value, certificate_value, votes_value

    def __search_movies(self, lock, url, index, movies, filters) -> None:
        start = (index * 50) + 1
        rankings_page = requests.get(url % start)
        rankings_list_soup = BeautifulSoup(rankings_page.text, "html.parser")
        rankings_soup = rankings_list_soup.find_all("div", class_="lister-item-content")

        year_filter, rating_filter, duration_filter = filters

        for ranking in rankings_soup:
            ranking_information = self.__get_movie_information(ranking)
            movie = Movie(*ranking_information)

            if year_filter is not None:
                if year_filter[0] == ">":
                    if movie.year < year_filter[1]:
                        continue
                elif year_filter[0] == "<":
                    if movie.year > year_filter[1]:
                        continue

            if rating_filter is not None:
                if rating_filter[0] == ">":
                    if movie.rating < rating_filter[1]:
                        continue
                elif rating_filter[0] == "<":
                    if movie.rating > rating_filter[1]:
                        continue

            if duration_filter is not None:
                if duration_filter[0] == ">":
                    if movie.duration < duration_filter[1]:
                        continue
                elif duration_filter[0] == "<":
                    if movie.duration > duration_filter[1]:
                        continue

            with lock:
                movies.append(movie)


    def get_movies(self) -> list:
        movies = []

        url = self.__get_url()
        total_rankings = self.__get_total_results(url, 1)
        filters = self.__get_movie_filter_options()
        year_filter, rating_filter, duration_filter = filters
        filter_string = ""

        if year_filter is not None:
            filter_string += f"\n\tmovie year is {year_filter[0]} {year_filter[1]}"

        if rating_filter is not None:
            filter_string += f"\n\tmovie rating is {rating_filter[0]} {rating_filter[1]}"

        if duration_filter is not None:
            filter_string += f"\n\tmovie duration is {duration_filter[0]} {duration_filter[1]}"

        if not filter_string:
            print("Filter Options:\n\tNone")
        else:
            print("Filter Options:", filter_string)

        print(f"\nSearching through {total_rankings} movies...")

        thread_number = total_rankings // 50 if total_rankings % 50 == 0 else (total_rankings // 50) + 1

        lock = threading.Lock()
        threads = [threading.Thread(target=self.__search_movies, args=(lock, url, i, movies, filters)) for i in range(thread_number)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        print(f"Found {len(movies)} matches:\n")
        return movies

    def get_tv_shows(self) -> list:
        shows = []
        i = 1

        url = self.__get_url()
        total_rankings = self.__get_total_results(url, 1)
        year_filter, rating_filter, discontinued_filter = self.__get_tv_show_filter_options()
        filter_string = ""

        if year_filter is not None:
            filter_string += f"\n\tshow start year is {year_filter[0]} {year_filter[1]}"

        if rating_filter is not None:
            filter_string += f"\n\tshow rating is {rating_filter[0]} {rating_filter[1]}"

        if discontinued_filter is not None:
            if discontinued_filter != False:
                filter_string += f"\n\tincluding discontinued shows"
            else:
                filter_string += f"\n\tnot including discontinued shows"

        if not filter_string:
            print("Filter Options:\n\tNone")
        else:
            print("Filter Options:", filter_string)

        print(f"\nSearching through {total_rankings} shows...")

        while True:
            rankings_page = requests.get(url % i)
            rankings_list_soup = BeautifulSoup(rankings_page.text, "html.parser")
            rankings_soup = rankings_list_soup.find_all("div", class_="lister-item-content")

            if i > total_rankings:
                break

            for ranking in rankings_soup:

                i += 1

                ranking_information = self.__get_tv_show_information(ranking)
                show = Show(*ranking_information)

                if year_filter is not None:
                    if year_filter[0] == ">":
                        if show.year[0] < year_filter[1]:
                            continue
                    elif year_filter[0] == "<":
                        if show.year[0] > year_filter[1]:
                            continue

                if rating_filter is not None:
                    if rating_filter[0] == ">":
                        if show.rating < rating_filter[1]:
                            continue
                    elif rating_filter[0] == "<":
                        if show.rating > rating_filter[1]:
                            continue

                if discontinued_filter is not None:
                    if discontinued_filter == False:
                        if show.discontinued != discontinued_filter:
                            continue

                shows.append(show)

        print(f"Found {len(shows)} matches:\n")
        return shows
