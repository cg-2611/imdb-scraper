import sys

from scraper import Types
from scraper import IMDbScraper


# parse the command line arguments
def get_args() -> tuple:
    movie_flag = True if "-m" in sys.argv else False
    tv_flag = True if "-t" in sys.argv else False

    if movie_flag and not tv_flag:
        content_type = Types.MOVIE
    elif tv_flag and not movie_flag:
        content_type = Types.TV_SHOW
    else:
        raise ValueError(f"invalid viewing medium provided, try using the \"-m\" option for {Types.MOVIE.value[0]}s or \
                           the \"-t\" option for {Types.TV_SHOW.value[0]}s")

    top_rated_flag = True if "-h" in sys.argv else False
    most_popular_flag = True if "-p" in sys.argv else False

    if top_rated_flag and not most_popular_flag:
        ranking_type = Types.TOP_RATED
    elif most_popular_flag and not top_rated_flag:
        ranking_type = Types.MOST_POPULAR
    else:
        raise ValueError(f"invalid chart type provided, try using the \"-h\" option for the {Types.TOP_RATED.value[0]} \
                           charts or the \"-p\" option for the {Types.MOST_POPULAR.value[0]} charts")

    genre_index = sys.argv.index("-g") if "-g" in sys.argv else -1
    genre = sys.argv[genre_index + 1] if genre_index != -1 else None

    votes_index = sys.argv.index("-v") if "-v" in sys.argv else -1
    votes = int(sys.argv[votes_index + 1]) if votes_index != -1 else 0

    limit_index = sys.argv.index("-n") if "-n" in sys.argv else -1
    limit = int(sys.argv[limit_index + 1]) if limit_index != -1 else 0

    filter_index = sys.argv.index("-f") if "-f" in sys.argv else -1
    filter = sys.argv[filter_index + 1] if filter_index != -1 else None

    return content_type, ranking_type, genre, votes, limit, filter

# if any valid filters are provided, print them
def print_movie_filter_options(filter_options: tuple) -> None:
    year_filter, rating_filter, duration_filter, gross_filter = filter_options
    filter_string = ""

    if year_filter is not None:
        filter_string += f"\n\tmovie year is {year_filter[0]} {year_filter[1]}"

    if rating_filter is not None:
        filter_string += f"\n\tmovie rating is {rating_filter[0]} {rating_filter[1]}"

    if duration_filter is not None:
        filter_string += f"\n\tmovie duration is {duration_filter[0]} {duration_filter[1]}"

    if gross_filter is not None:
        filter_string += f"\n\tmovie gross is {gross_filter[0]} {gross_filter[1]}"

    if not filter_string:
        print("Filter Options:\n\tNone")
    else:
        print("Filter Options:", filter_string)

# if any valid filters are provided, print them
def print_tv_show_filter_options(filters: tuple) -> None:
    year_filter, rating_filter, discontinued_filter = filters
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

# print the movies from the list in a table
def print_movies(movies: list) -> None:
    if movies:
        # get the length of the longest name of a movie
        max_length = max(len(movie.name) for movie in movies)

        # calculate the number of tab characters needed to maintained uniform spacing
        tab_characters = (max_length // 8) + 1

        # pad the header
        name_header = "Name" + ("\t" * tab_characters)

        headings = f"\tRank\t {name_header} Year\t Rating Duration Cert.\t Votes\t Gross"

        print(headings)
        print()

        for i, movie in enumerate(movies):
            # pad any movie names shorter than the longest so that the column width in maintained
            if (len(movie.name) + 1) % 8 == 0:
                name_string = movie.name + ("\t" * ((tab_characters - (len(movie.name) // 8)) - 1))
            else:
                name_string = movie.name + ("\t" * (tab_characters - (len(movie.name) // 8)))

            # pad the number of votes with tab characters if it is too short
            if len(str(movie.votes)) < 7:
                votes_string = str(movie.votes) + "\t"
            else:
                votes_string = str(movie.votes)

            # if the movie has a gross value, pre-pend it with a '$'
            if movie.gross is not None:
                gross_string = "$" + str(movie.gross)
            else:
                gross_string = str(movie.gross)

            # print the movie information
            print(f"{i + 1}.\t{movie.rank}\t {name_string} {movie.year}\t {movie.rating}\t{movie.duration}\t {movie.certificate}\t {votes_string} {gross_string}")
    else:
        print("No Matches")

def print_tv_shows(shows: list) -> None:
    if shows:
        # get the length of the longest name of a show
        max_length = max(len(show.name) for show in shows)

        # calculate the number of tab characters needed to maintained uniform spacing
        tab_characters = (max_length // 8) + 1

        # pad the header
        name_header = "Name" + ("\t" * tab_characters)

        headings = f"\tRank\t {name_header} Start End\t Rating Cert.\t Discont. Votes"

        print(headings)
        print()

        for i, show in enumerate(shows):
            # pad any show names shorter than the longest so that the column width in maintained
            if (len(show.name) + 1) % 8 == 0:
                name_string = show.name + ("\t" * ((tab_characters - (len(show.name) // 8)) - 1))
            else:
                name_string = show.name + ("\t" * (tab_characters - (len(show.name) // 8)))

            # print the show information
            print(f"{i + 1}.\t{show.rank}\t {name_string} {show.year[0]}  {show.year[1]}\t {show.rating}\t {show.certificate}\t {show.discontinued}\t  {show.votes}")
    else:
        print("No matches")

def main() -> None:
    args = get_args()
    scraper = IMDbScraper(*args)

    if args[0] == Types.MOVIE:
        # print the valid filter options
        filter_options = scraper.get_movie_filter_options()
        print_movie_filter_options(filter_options)

        # output the number of movies being searched through
        search_total = scraper.get_search_total()
        print(f"\nSearching through {search_total} movies...")

        # perform the search
        movie_results = scraper.get_movies()

        # output the results
        print(f"Found {len(movie_results)} matches:\n")
        print_movies(movie_results)
    elif args[0] == Types.TV_SHOW:
        # print the valid filter options
        filter_options = scraper.get_tv_show_filter_options()
        print_tv_show_filter_options(filter_options)

        # output the number of shows being searched through
        search_total = scraper.get_search_total()
        print(f"\nSearching through {search_total} shows...")

        # perform the search
        tv_show_results = scraper.get_tv_shows()

        # output the results
        print(f"Found {len(tv_show_results)} matches:\n")
        print_tv_shows(tv_show_results)


if __name__ == "__main__":
    main()
