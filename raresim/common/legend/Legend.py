class Legend:
    SUPPORTED_COLUMNS = ["id", "position", "a0", "a1", "prob", "protected", "fun"]

    def __init__(self, header: list):
        self.__header = header
        self.__rows = []

    def get_header(self) -> list:
        """
        Getter for the header of the legend
        @return: legend header
        """
        return self.__header

    def row_count(self) -> int:
        """
        Getter for the number of rows in the legend
        @return: number of rows in the legend
        """
        return len(self.__rows)

    def add_row(self, row: list) -> None:
        """
        Adds a row to the Legend
        @param row: The row to add (as a list)
        @return: None
        """
        # TODO: Add validation that the row format matches that of self.__header
        self.__rows.append(row)

    def remove_row(self, index: int) -> list:
        """
        Removes a row from the legend and returns the removed row
        @param index: 0-based index of the row to remove
        @return: the removed row
        """
        return self.__rows.pop(index)

    def get_row(self, index: int) -> dict:
        """
        Gets a map of header_field -> row_value for a requested row
        @param index: 0-based index of the requested row
        @return: A map of header_field -> row_value for a requested row
        """
        return dict(zip(self.__header, self.__rows[index]))
