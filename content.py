class Movie:
    def __init__(self, name: str, year: int, rank: int, rating: float, duration: int, certificate: str, votes: str, gross: str) -> None:
        self.name = name
        self.year = year
        self.rank = rank
        self.rating = rating
        self.duration = duration
        self.certificate = certificate
        self.votes = votes
        self.gross = gross
