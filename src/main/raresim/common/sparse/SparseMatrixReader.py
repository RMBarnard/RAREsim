import os
import gzip
import timeit
import numpy as np

from src.main.raresim.common.sparse import SparseMatrix
from src.main.raresim.common.exceptions import IllegalArgumentException


class SparseMatrixReader:
    def __init__(self):
        pass

    def loadSparseMatrix(self, filepath: str) -> SparseMatrix:
        if not os.path.isfile(filepath):
            raise IllegalArgumentException(f"No such file exists: {filepath}")
        if filepath[-3:] == '.sm':
            return self.__loadCompressed(filepath)
        elif filepath[-3:] == '.gz':
            return self.__loadZipped(filepath)
        return self.__loadUncompressed(filepath)

    def __loadZipped(self, filepath: str) -> SparseMatrix:
        with gzip.open(filepath, "rt") as f:
            line = f.readline()
            nums = np.fromstring(line, dtype=int, sep=" ")
            matrix = SparseMatrix(len(nums))
            matrix.add_row(self.__getSparseRow(nums))

            while True:
                line = f.readline()

                if line is None or line.strip() == "\n" or line.strip() == '':
                    break

                nums = np.fromstring(line, dtype=int, sep=" ")

                row_to_add = self.__getSparseRow(nums)

                matrix.add_row(row_to_add)
        return matrix

    def __loadCompressed(self, filepath: str) -> SparseMatrix:
        with open(filepath, "rb") as f:
            data = f.read(4)
            matrix = SparseMatrix(int.from_bytes(data, "little"))
            row = []
            data = f.read(4)
            while data:
                if self.__toSigned32(int.from_bytes(data, "little")) == -1:
                    matrix.add_row(row)
                    row = []
                else:
                    row.append(int.from_bytes(data, "little"))
                data = f.read(4)
        return matrix

    def __loadUncompressed(self, filepath: str) -> SparseMatrix:
        with open(filepath, "r") as f:
            line = f.readline()
            nums = np.fromstring(line, dtype=int, sep=" ")
            matrix = SparseMatrix(len(nums))
            matrix.add_row(self.__getSparseRow(nums))
            while True:
                line = f.readline()
                if line is None or line.strip() == "\n" or line.strip() == '':
                    break
                nums = np.fromstring(line, dtype=int, sep=" ")
                matrix.add_row(self.__getSparseRow(nums))
        return matrix

    def __getSparseRow(self, nums: np.ndarray) -> list:
        return np.where(nums == 1)[0]

    def __toSigned32(self, n):
        n = n & 0xffffffff
        return n | (-(n & 0x80000000))
