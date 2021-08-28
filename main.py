import sys

from scraper import Types
from scraper import IMDbScraper


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

def print_movies(movies: list) -> None:
    if movies:
        print(f"Found {len(movies)} matches:\n")

        max_length = max(len(movie.name) for movie in movies)

        tab_characters = (max_length // 8) + 1
        name_header = "Name" + ("\t" * tab_characters)

        headings = f"\tRank\t {name_header} Year\t Rating Duration Cert.\t Votes\t Gross"

        print(headings)
        print()

        for i, movie in enumerate(movies):
            if (len(movie.name) + 1) % 8 == 0:
                name_string = movie.name + ("\t" * ((tab_characters - (len(movie.name) // 8)) - 1))
            else:
                name_string = movie.name + ("\t" * (tab_characters - (len(movie.name) // 8)))

            if len(str(movie.votes)) < 7:
                votes_string = str(movie.votes) + "\t"
            else:
                votes_string = str(movie.votes)

            if movie.gross is not None:
                gross_string = "$" + str(movie.gross)
            else:
                gross_string = str(movie.gross)

            print(f"{i + 1}.\t{movie.rank}\t {name_string} {movie.year}\t {movie.rating}\t{movie.duration}\t {movie.certificate}\t {votes_string} {gross_string}")
    else:
        print("No Matches")

def print_shows(shows: list) -> None:
    if shows:
        print(f"Found {len(shows)} matches:\n")

        max_length = max(len(show.name) for show in shows)

        tab_characters = (max_length // 8) + 1
        name_header = "Name" + ("\t" * tab_characters)

        headings = f"\tRank\t {name_header} Start End\t Rating Cert.\t Discont. Votes"

        print(headings)
        print()

        for i, show in enumerate(shows):
            if (len(show.name) + 1) % 8 == 0:
                name_string = show.name + ("\t" * ((tab_characters - (len(show.name) // 8)) - 1))
            else:
                name_string = show.name + ("\t" * (tab_characters - (len(show.name) // 8)))

            print(f"{i + 1}.\t{show.rank}\t {name_string} {show.year[0]}  {show.year[1]}\t {show.rating}\t {show.certificate}\t {show.discontinued}\t  {show.votes}")
    else:
        print("No matches")

def main() -> None:
    args = get_args()
    scraper = IMDbScraper(*args)

    if args[0] == Types.MOVIE:
        movie_results = scraper.get_movies()
        print_movies(movie_results)
    elif args[0] == Types.TV_SHOW:
        tv_show_results = scraper.get_tv_shows()
        print_shows(tv_show_results)



if __name__ == "__main__":
    main()
