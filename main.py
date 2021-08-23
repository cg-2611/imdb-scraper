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

    top_rated_flag = True if "-c" in sys.argv else False
    most_popular_flag = True if "-p" in sys.argv else False

    if top_rated_flag and not most_popular_flag:
        ranking_type = Types.TOP_RATED
    elif most_popular_flag and not top_rated_flag:
        ranking_type = Types.MOST_POPULAR
    else:
        raise ValueError(f"invalid chart type provided, try using the \"-c\" option for the {Types.TOP_RATED.value[0]} \
                           charts or the \"-p\" option for the {Types.MOST_POPULAR.value[0]} charts")

    genre_index = sys.argv.index("-g") if "-g" in sys.argv else -1
    genre = sys.argv[genre_index + 1] if genre_index != -1 else None

    votes_index = sys.argv.index("-v") if "-v" in sys.argv else -1
    votes = int(sys.argv[votes_index + 1]) if votes_index != -1 else 0

    limit_index = sys.argv.index("-n") if "-n" in sys.argv else -1
    limit = int(sys.argv[limit_index + 1]) if limit_index != -1 else 0

    return content_type, ranking_type, genre, votes, limit

def main() -> None:
    args = get_args()
    scraper = IMDbScraper(*args)

    if args[0] == Types.MOVIE:
        movie_results = scraper.get_movies()
        for movie in movie_results:
                print(f"{movie.rank}\t{movie.name}\t{movie.year}\t{movie.rating}\t{movie.duration}\t{movie.certificate}\t{movie.votes}\t{movie.gross}")
    elif args[0] == Types.TV_SHOW:
        tv_show_results = scraper.get_tv_shows()
        for show in tv_show_results:
                print(f"{show.rank}\t{show.name}\t{show.year}\t{show.rating}\t{show.certificate}\t{show.votes}\t{show.discontinued}")



if __name__ == "__main__":
    main()
