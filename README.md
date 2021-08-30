# IMDb Web Scraper

This is a multithreaded web scraper that extracts information about movies and tv shows from pages on [IMDb](https://www.imdb.com/).
Multithreading is used to search through multiple sections concurrently and improve the search time. It can be used to collect films that meet the user's search criteria.

`main.py` is a program that can be run to output the scraping results in a table and `scraper.py` contains the classes used to perform the web scraping.


### Run
---
Clone repository with:
```
git clone https://github.com/cg-2611/imdb-scraper.git
```
Navigate to the directory created:
```
cd imdb-scraper
```
Run the program with:
```
python main.py [required arguments] [optional arguments]
```
For example:
```
python main.py -m -h -g comedy -v 50000 -n 1000
```
will produce resutls after searching the top 1000 comedy movies with more than 500000 votes in the top rated charts.

> Note: the program is written using python 3 and so the `python3` command may be required instead.
>
> Note: the program requires the requests package and the beautifulesoup4 package. These can be installed with any package manager, using the project Pipfile or using pip, for example:
> ```
> pip install requests beautifulsoup4
> ```


### Arguments
---
Required arguments:
- `-m` or `-t`: used to control whether the search yields movies (`-m`) or tv shows (`-t`).
- `-h` or `-p`: used to control where the search takes the results from either the highest rated charts (`-h`) or the current most popular charts (`-p`).

Optional arguments:
- `-g <genre>`: used to search for content of a particular genre if it is a valid genre that IMDb recognises for the specified content type. If not specified, results will be of any genre.
- `-v <number_of_votes>`: used to control the minimum number of votes a movie or tv show must have to be considered in the search. If no value is specified, the default for a movie is 25000 and the default for a tv show is 5000.
- `-n <maximum_search_number>`: used to control how many movies or tv shows will be searched through. If not specified, the search will be carried out on possible rankings given other restrictions such as genre and number of votes.
- `-f "<filter_options>"`: used to add more criteria to narrow the search. Filter options must be inside double quotes and each should be separated by a space. If not specified, no filter options will be applied (see below for more information).

Example: `-g action -v 100000 -n 100` will search through the first 100 action movies or tv shows with more 100000 votes.

Movie filter options:
- Movie duration: specified using a 'd' followed by either '<' or '>' and finally the value of the movie duration (in minutes)
- Movie rating: specified using an 'r' followed by either '<' or '>' and finally the value of the movie rating
- Movie year: specified using a 'y' followed by either '<' or '>' and finally the value of the movie release year
- Movie gross: specified using a 'g' followed by either '<' or '>' and finally the value of the movie gross (in USD)

Example: `-f "d>150 r>8.6 y<2007 g>150000000"` will search for films with a duration greater than 150 minutes, have a rating of at least 8.7, have been released no later than 2006 and have grossed over 150 million USD.

TV show filter options:
- Show discontinued filter: specified using a 'd' followed by '=True' or '=False'. Using '=False' will only include shows that are still running in the search. The default behaviour is to include all shows.
-  Show rating: specified using an 'r' followed by either '<' or '>' and finally the value of the show rating
-  Show start year: specified using 'y' followed by either '<' or '>' and finally the value of show start year

Example: `-f "d=False r>8.6 y<2007"` will search for show that are still running that have a rating of at least 8.7 and began airing no later than 2006.
