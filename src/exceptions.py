class KufarScraperError(Exception):
    def __init__(self, message: str = "Something went wrong."):
        super().__init__(message)


class KufarScraperNetworkError(KufarScraperError):
    def __init__(self, message: str = "Network error"):
        super().__init__(message)


class KufarScraperDatabaseError(KufarScraperError):
    def __init__(self, message: str = "Database error"):
        super().__init__(message)
