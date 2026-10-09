class ParseError(Exception):
    def __init__(self, message: str, line: int | None = None) -> None:
        self.line = line
        super().__init__(f"Line {line}: {message}" if line else message)
