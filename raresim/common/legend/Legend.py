class Legend:
    supported_columns = ["id", "position", "a0", "a1", "prob", "protected", "fun"]

    def __init__(self, header: list):
        self.__header = header
        self.__rows = []

    def get_header(self) -> list:
        return self.__header

    def row_count(self) -> int:
        return len(self.__rows)

    def add_row(self, row: list) -> None:
        self.__rows.append(row)

    def remove_row(self, index: int) -> None:
        self.__rows.pop(index)

    def get_row(self, index: int) -> dict:
        return dict(zip(self.__header, self.__rows[index]))
