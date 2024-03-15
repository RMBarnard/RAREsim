from src.main.raresim.common.exceptions.RaresimException import RaresimException
import random


class SparseMatrix:
    """
    A sparse matrix is a matrix of 0s and 1s in which most of the values are 0s.
    It stores the data efficiently by simply storing the indices of each 1 rather than storing all the 1s and 0s
    of the matrix. The __data field is a list of "rows" where each "row" is a list the indices where a 1 is present
    in that row.
    """

    def __init__(self, cols=0):
        self.__cols = cols
        self.__rows = 0
        self.__data = []

    def set_col_count(self, cols: int) -> None:
        """
        Only to be used by binary reader to set the number of columns when creating SparseMatrix object
        @param cols: number of cols
        @return: None
        """

    def get(self, row: int, col: int) -> int:
        """
        Gets the value in the matrix at a requested position
        @param row: index of row
        @param col: index of column
        @return: value at requested position
        """
        if row > self.__rows or col > self.__cols:
            raise RaresimException(
                f"Attempted to get value at {row},{col} when the bounds of the matrix were {self.__rows},{self.__cols}")

        arr = self.__data[row]
        # Use binary search to search for the presence of the index in O(log(n)) time
        low = 0
        high = len(arr) - 1
        while low <= high:
            mid = (high + low) // 2
            if arr[mid] < col:
                low = mid + 1
            elif arr[mid] > col:
                high = mid - 1
            else:
                # Return 1 if index is present
                return 1
        # If we reach here, then the index was not present so the value at the requested position is a 0
        return 0

    def get_row(self, row: int) -> list:
        """
        Gets the full row at the requested index
        @param row: index of row to get
        @return: the full row at the requested index
        """
        if row > self.__rows:
            raise RaresimException(f"Attempted to get row {row}, but there are only {self.__rows} rows")
        ret = [0] * self.__cols
        for i in self.__data[row]:
            ret[i] = 1
        return ret

    def get_row_raw(self, row: int) -> list:
        """
        Gets the indicies of the ones in a row
        @param row: index of row to get
        @return: list of the indicies of the ones in a row
        """
        return self.__data[row].tolist()

    def add(self, row: int, col: int) -> None:
        """
        Adds a 1 to the matrix at the given location.
        @param row: row to insert the value
        @param col: column to insert the one at
        @return:
        """
        if col > self.__cols:
            raise Exception(f"Attempted to insert at column {col}, but the matrix only has {self.__cols} columns")
        while row > len(self.__data):
            self.__data.append(())
            self.__rows += 1
        temp = self.__data[row]
        temp.append(col)
        temp.sort()
        temp = list(set(temp))
        self.__data[row] = temp

    def remove(self, row: int, col: int) -> None:
        """
        Places a zero at the given position
        @param row: row index
        @param col: column index
        @return: None
        """
        self.__data[row].remove(col)


    def add_row(self, val: list) -> None:
        """
        Sets row at given index to the provided list. Only to be used by SparseMatrixReader
        @param val: list of indices representing locations of 1s in the new row
        @return: None
        """
        self.__data.append(val)
        self.__rows += 1

    def remove_row(self, row: int) -> None:
        """
        Removes the row at the given index
        @param row: index of the row to remove
        @return: None
        """
        self.__data.pop(row)
        self.__rows -= 1

    def num_rows(self) -> int:
        """
        @return: the number of rows in the matrix
        """
        return self.__rows

    def num_cols(self) -> int:
        """
        @return: the number of columns in the matrix
        """
        return self.__cols

    def row_num(self, row: int) -> int:
        """
        @param row: index of row
        @return: the number of 1s in the requested row
        """
        if row > self.__rows - 1:
            raise RaresimException(f"Attempted to access row {row} but there were only{self.__rows} in the matrix")
        return len(self.__data[row])

    def prune_row(self, row: int, num_prune: int) -> None:
        """
        Randomly prunes n 1s from the given row
        @param row: index of the row to prune
        @param num_prune: how many 1s to prune from the row
        @return: None
        """
        if row > self.__rows:
            return

        num_keep = len(self.__data[row]) - num_prune
        keep_ids = self.__reservoir_sample(num_keep, len(self.__data[row]))
        keep_ids.sort()
        ret = []
        for i in keep_ids:
            ret.append(self.__data[row][i])

        self.__data[row] = ret

    def __reservoir_sample(self, k: int, n: int) -> list:
        """
        @param k: desired size of sample
        @param n: max size of any element + 1
        @return: random sample of k elements in the range [0...n-1]
        """
        stream = [i for i in range(n)]
        reservoir = [0] * k
        i = 0
        for i in range(k):
            reservoir[i] = stream[i]

        while i < n:
            j = random.randrange(i + 1)
            if j < k:
                reservoir[j] = stream[i]
            i += 1
        return reservoir
