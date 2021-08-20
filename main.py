import sys

import requests

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
        raise ValueError(f"invalid viewing medium provided, try using the \"-m\" option for {Types.MOVIE.value}s or \
                           the \"-t\" option for {Types.TV_SHOW.value}s")

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

    return content_type, ranking_type, genre

def main() -> None:
    content_type, ranking_type, genre = get_args()

    scraper = IMDbScraper(content_type, ranking_type, genre)

    movie_results = scraper.get_movies()

    for result in movie_results:
        if result.duration > 150:
            print(f"{result.rank}\t{result.name}\t{result.year}\t{result.rating}\t{result.duration}\t{result.certificate}\t{result.votes}\t{result.gross}")


if __name__ == "__main__":
    main()
