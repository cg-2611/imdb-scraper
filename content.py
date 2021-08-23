class Movie:
    def __init__(self, name: str, year: int, rank: int, rating: float, duration: int, certificate: str, votes: int, gross: int) -> None:
        self.name = name
        self.year = year
        self.rank = rank
        self.rating = rating
        self.duration = duration
        self.certificate = certificate
        self.votes = votes
        self.gross = gross

class Show:
    def __init__(self, name: str, year: tuple, discontinued: bool, rank: int, rating: float, certificate: str, votes: int) -> None:
        self.name = name
        self.year = year
        self.discontinued = discontinued
        self.rank = rank
        self.rating = rating
        self.certificate = certificate
        self.votes = votes
