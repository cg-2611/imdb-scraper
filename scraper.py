import requests
import threading

from enum import Enum

from bs4 import BeautifulSoup
from bs4 import PageElement

URL = "https://www.imdb.com/search/title/"


class Types(Enum):
    MOVIE = ["movie", "feature"]
    TV_SHOW = ["tv-show", "tv_series,tv_miniseries"]
    TOP_RATED = ["top-rated"]
    MOST_POPULAR = ["most-popular"]


class Movie:
    """
    Movie class stores information about a movie.
    """
    def __init__(self, name: str, year: int, rank: int, rating: float, duration: int, certificate: str, votes: int, gross: int) -> None:
        """
        Constructor for Movie, creates a new instance of a Movie.

        :param name: the name of the movie
        :param year: the year the movie was released
        :param rank: the imdb rank on the list of rankings of the movie
        :param rating: the imdb rating of the movie
        :param duration: the length of the movie in minutes
        :param certificate: the certificate of the movie
        :param votes: the number of votes the movie has
        :param gross: the amount of money the movie grossed
        """
        self.name = name
        self.year = year
        self.rank = rank
        self.rating = rating
        self.duration = duration
        self.certificate = certificate
        self.votes = votes
        self.gross = gross


class Show:
    """
    Show class stores information about a show.
    """
    def __init__(self, name: str, year: tuple, discontinued: bool, rank: int, rating: float, certificate: str, votes: int) -> None:
        """
        Constructor for Show, creates a new instance of a Show.

        :param name: the name of the show
        :param year: a tuple containing the year the show started airing and the year it stopped if applicable
        :para discontinued: a boolean that represents whether or not the show is still running
        :param rank: the imdb rank on the list of rankings of the show
        :param rating: the imdb rating of the show
        :param certificate: the certificate of the show
        :param votes: the number of votes the show
        """
        self.name = name
        self.year = year
        self.discontinued = discontinued
        self.rank = rank
        self.rating = rating
        self.certificate = certificate
        self.votes = votes


class IMDbScraper:
    """
    IMDbScraper is a multithreaded web scraper that search for movies and tv shows on IMDb's website.
    """
    def __init__(self, content_type: Types, ranking_type: Types, genre:str, votes:int, limit: int, filter: str) -> None:
        """
        Constructor for IMDbScraper, creates a new instance of an IMDbScraper class.

        :param content_type: either Types.MOVIE or Types.TV_SHOW, and controls which specific web pages will be scraped
        :param ranking_type: either Types.TOP_RATED or Types.MOST_POPULAR, and controls which type of rankings page will be searched
        :param genre: the genre of content that will be searched for, can be None to search all genres
        :param votes: the minimum number of votes that a movie or tv show will have to be considered in a search
        :param limit: the number of movies or tv shows that will be considered when searching
        :param filter: the filter options used to make the search more narrow
        """
        self.content_type = content_type
        self.ranking_type = ranking_type
        self.genre = genre

        if self.content_type == Types.MOVIE:
            self.votes = votes if votes > 1 else 25000
        elif self.content_type == Types.TV_SHOW:
            self.votes = votes if votes > 1 else 5000

        self.limit = limit if limit > 1 else None
        self.filter = filter

        self.genres = [genre for genre in self.__get_genres()]

    def get_movies(self) -> list:
        """
        Creates and starts the threads used to search through the content rankings and performs the search.

        :return: the list of movies that meet the search criteria
        """
        movies = []

        url = self.__get_url()
        search_total = self.__get_total_results(url)
        filters = self.get_movie_filter_options()

        # calculate the number of threads needed so that one thread will search one page,
        # 50 is used since IMDb has 50 results per page
        thread_number = search_total // 50 if search_total % 50 == 0 else (search_total // 50) + 1

        # the maximum number of movies the final thread will search
        # e.g. if the user is search through the top 75 movies, there will be two threads, the first searching through
        # 50 movies, and the second searching through the reamining 25, the value of final_thread_total being 25
        final_thread_total = search_total - ((thread_number - 1) * 50)

        # create a list of threads that will search all 50 movies on each page
        threads = [threading.Thread(target=self.__search_movies, args=(url, movies, filters, 50)) for _ in range(thread_number - 1)]

        # append the final thread to the list that will search the final page
        threads.append(threading.Thread(target=self.__search_movies, args=(url, movies, filters, final_thread_total)))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # sort the list of movies by the IMDb rank in the list of rankings
        movies.sort(key=lambda movie: movie.rank)
        return movies

    def get_tv_shows(self) -> list:
        """
        Creates and starts the threads used to search through the content rankings and performs the search.

        :return: the list of shows that meet the search criteria
        """
        shows = []

        url = self.__get_url()
        total_rankings = self.__get_total_results(url)
        filters = self.get_tv_show_filter_options()

        # calculate the number of threads needed so that one thread will search one page,
        # 50 is used since IMDb has 50 results per page
        thread_number = total_rankings // 50 if total_rankings % 50 == 0 else (total_rankings // 50) + 1

        # the maximum number of shows the final thread will search
        # e.g. if the user is search through the top 75 shows, there will be two threads, the first searching through
        # 50 shows, and the second searching through the reamining 25, the value of final_thread_total being 25
        final_thread_total = total_rankings - ((thread_number - 1) * 50)

        # create a list of threads that will search all 50 movies on each page
        threads = [threading.Thread(target=self.__search_tv_shows, args=(url, shows, filters, 50)) for _ in range(thread_number - 1)]

        # append the final thread to the list that will search the final page
        threads.append(threading.Thread(target=self.__search_tv_shows, args=(url, shows, filters, final_thread_total)))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # sort the list of movies by the IMDb rank in the list of rankings
        shows.sort(key=lambda show: show.rank)
        return shows

    def get_movie_filter_options(self) -> tuple:
        """
        Parses the movie filter options and creates a tuple of the useful information.

        :return: tuple containing the filters that will be applied when searching through movies
        """
        year_filter, rating_filter, duration_filter, gross_filter = None, None, None, None

        if self.filter is not None:
            filter_options = self.filter.split()

            for option in filter_options:
                # option[1] contains either '<' or '>' and option[2:] will be the value

                if option.startswith("y"):
                    year_filter = [option[1], int(option[2:])]
                    continue

                if option.startswith("r"):
                    rating_filter = [option[1], float(option[2:])]
                    continue

                if option.startswith("d"):
                    duration_filter = [option[1], int(option[2:])]
                    continue

                if option.startswith("g"):
                    gross_filter = [option[1], int(option[2:])]
                    continue

        return (year_filter, rating_filter, duration_filter, gross_filter)

    def get_tv_show_filter_options(self) -> tuple:
        """
        Parses the movie filter options and creates a tuple of the useful information.

        :return: tuple containing the filters that will be applied when searching through shows
        """
        year_filter, rating_filter, discontinued_filter = None, None, None

        if self.filter is not None:
            filter_options = self.filter.split()

            for option in filter_options:

                # for year and rating, option[1] contains either '<' or '>' and option[2:] will be the value
                if option.startswith("y"):
                    year_filter = [option[1], int(option[2:])]
                    continue

                if option.startswith("r"):
                    rating_filter = [option[1], float(option[2:])]
                    continue

                # for discontinued filter, check the value after the '=' and return the corresponding boolean value
                if option.startswith("d"):
                    value_index = option.find("=")
                    value = option[value_index + 1:]
                    discontinued_filter = False if value == "False" else True
                    continue

        return (year_filter, rating_filter, discontinued_filter)

    def get_search_total(self) -> int:
        """
        :return: the total number of movies or tv shows that will be searched through.
        """
        return self.__get_total_results(self.__get_url())

    def __search_movies(self, url: str, movies: list, filters: tuple, total: int) -> None:
        # get the index of the current thread an use it to calculate which page the thread will be searching through
        current_thread = threading.current_thread()
        index = int("".join(filter(str.isdigit, current_thread.name))) - 1
        start = (index * 50) + 1

        # perform the scraping on the page
        rankings_page = requests.get(url % start)
        rankings_list_soup = BeautifulSoup(rankings_page.text, "html.parser")
        rankings_soup = rankings_list_soup.find_all("div", class_="lister-item-content")

        year_filter, rating_filter, duration_filter, gross_filter = filters

        searched = 0
        for ranking in rankings_soup:
            searched += 1
            if searched > total:
                break

            # parse the ranking and extract the information
            ranking_information = self.__get_movie_information(ranking)

            # create a Movie object to store the information
            movie = Movie(*ranking_information)

            # check the filter criteria against the movie
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

            if gross_filter is not None:
                if movie.gross is None:
                    continue

                if gross_filter[0] == ">":
                    if movie.gross < gross_filter[1]:
                        continue
                elif gross_filter[0] == "<":
                    if movie.gross > gross_filter[1]:
                        continue

            # if the movie meets all the criteria, append it to the list of movies
            movies.append(movie)

    def __search_tv_shows(self, url: str, shows: list, filters: tuple, total: int) -> None:
        # get the index of the current thread an use it to calculate which page the thread will be searching through
        current_thread = threading.current_thread()
        index = int("".join(filter(str.isdigit, current_thread.name))) - 1
        start = (index * 50) + 1

        # perform the scraping on the page
        rankings_page = requests.get(url % start)
        rankings_list_soup = BeautifulSoup(rankings_page.text, "html.parser")
        rankings_soup = rankings_list_soup.find_all("div", class_="lister-item-content")

        year_filter, rating_filter, discontinued_filter = filters

        searched = 0
        for ranking in rankings_soup:
            searched += 1
            if searched > total:
                break

            # parse the ranking and extract the information
            ranking_information = self.__get_tv_show_information(ranking)

            # create a Show object to store the information
            show = Show(*ranking_information)

            # check the filter criteria against the show
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

            # if the show meets all the criteria, append it to the list of movies
            shows.append(show)

    def __get_movie_information(self, movie_soup: PageElement) -> tuple:
        # extract all the necessary information about a movie

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
        # extract all the necessary information about a tv show

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

    def __get_url(self) -> str:
        # return the url of the webpage to be scraped based on the attributes of the object
        if self.ranking_type == Types.TOP_RATED:
            return URL + f"?genres={self.genre}&sort=user_rating,desc&title_type={self.content_type.value[1]}&start=%d&num_votes={self.votes},"
        elif self.ranking_type == Types.MOST_POPULAR:
            return URL + f"?genres={self.genre}&title_type={self.content_type.value[1]}&start=%d&num_votes={self.votes},"

    def __get_genres(self) -> str:
        # extract each genre from a list of genres on IMDb's website
        genre_table_soup = self.__get_genres_list()
        genre_list_soup = genre_table_soup.find_all("div", class_="table-cell primary")

        for genre in genre_list_soup:
            yield genre.find("a").get_text().strip().lower().replace(" ", "-")

    def __get_genres_list(self) -> str:
        # get the html the genres page of IMDb to collect the lists of genres for each content type
        genre_page = requests.get("https://www.imdb.com/feature/genre/")
        genre_page_soup = BeautifulSoup(genre_page.text, "html.parser")

        genre_table_soup = genre_page_soup.find_all("div", class_="ab_links")

        # return the list of genres relevant to the chosen content type
        if self.content_type == Types.MOVIE:
            return genre_table_soup[0]
        elif self.content_type == Types.TV_SHOW:
            return genre_table_soup[1]

    def __get_total_results(self, url: str) -> int:
        # extract the total number of rnakings for the specified url and compare it to the limit attribute
        page_soup = BeautifulSoup(requests.get(url % 1).text, "html.parser")
        total_string = page_soup.find("div", class_="desc").find("span").get_text().replace(",", "")
        total = int("".join(filter(str.isdigit, total_string[total_string.find("of "):])))

        # if the limit attribute has a value, return the total number of rankings only if it is
        # less than the limit attribute
        if self.limit is None:
            return total
        else:
            return total if total < self.limit else self.limit
