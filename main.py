import sys

from scraper import Flags
from scraper import IMDbScraper


def get_args() -> tuple:
    movie_flag = True if "-m" in sys.argv else False
    tv_flag = True if "-t" in sys.argv else False

    if movie_flag and not tv_flag:
        viewing_medium = Flags.MOVIE
    elif tv_flag and not movie_flag:
        viewing_medium = Flags.TV_SHOW
    else:
        raise ValueError(f"invalid viewing medium provided, try using the \"-m\" option for {Flags.MOVIE.value}s or \
                           the \"-t\" option for {Flags.TV_SHOW.value}s")

    top_rated_flag = True if "-c" in sys.argv else False
    most_popular_flag = True if "-p" in sys.argv else False

    if top_rated_flag and not most_popular_flag:
        chart_type = Flags.TOP_RATED
    elif most_popular_flag and not top_rated_flag:
        chart_type = Flags.MOST_POPULAR
    else:
        raise ValueError(f"invalid chart type provided, try using the \"-c\" option for the {Flags.TOP_RATED.value[0]} \
                           charts or the \"-p\" option for the {Flags.MOST_POPULAR.value[0]} charts")

    genre_index = sys.argv.index("-g") if "-g" in sys.argv else -1
    genre = sys.argv[genre_index + 1] if genre_index != -1 else None

    return viewing_medium, chart_type, genre

def main() -> None:
    viewing_medium, chart_type, genre = get_args()

    scraper = IMDbScraper(viewing_medium, chart_type, genre)

    print(scraper.url)
    print(scraper.genres)


if __name__ == "__main__":
    main()
