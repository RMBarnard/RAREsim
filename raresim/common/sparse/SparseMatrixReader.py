import os
import gzip
import timeit
import numpy as np
import numba as nb

from raresim.common.sparse import SparseMatrix
from raresim.common.exceptions import IllegalArgumentException


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
            total = timeit.default_timer()
            line = f.readline()
            nums = self.compute(np.frombuffer(line[::2].encode('ascii'), np.uint8))
            matrix = SparseMatrix.SparseMatrix(len(nums))
            matrix.add_row(self.__getSparseRow(nums))
            i = 1

            while True:
                line = f.readline()
                if line is None or line.strip() == "\n" or line.strip() == '':
                    break
                nums = self.compute(np.frombuffer(line[::2].encode('ascii'), np.uint8))
                row_to_add = self.__getSparseRow(nums)
                matrix.add_row(row_to_add)
                i += 1

        print(f"Total time = {timeit.default_timer() - total}")
        return matrix

    def __loadCompressed(self, filepath: str) -> SparseMatrix:
        timer = timeit.default_timer()
        with open(filepath, "rb") as f:
            data = f.read(4)
            matrix = SparseMatrix(int.from_bytes(data, "little"))
            row = []
            data = f.read(4)
            while data:
                if self.__toSigned32(int.from_bytes(data, "little")) == -1:
                    matrix.add_row(np.fromiter(row, dtype=int))
                    row = []
                else:
                    row.append(int.from_bytes(data, "little"))
                data = f.read(4)
        print(f"Read file in {timeit.default_timer() - timer}")
        return matrix

    def __loadUncompressed(self, filepath: str) -> SparseMatrix:
        with open(filepath, "r") as f:
            line = f.readline()
            nums = self.compute(np.frombuffer(line.encode('ascii'), np.uint8))
            matrix = SparseMatrix(len(nums))
            matrix.add_row(self.__getSparseRow(nums))
            while True:
                line = f.readline()
                if line is None or line.strip() == "\n" or line.strip() == '':
                    break
                nums = self.compute(np.frombuffer(line.encode('ascii'), np.uint8))
                matrix.add_row(self.__getSparseRow(nums))
        return matrix

    def __getSparseRow(self, nums: np.ndarray) -> list:
        return np.where(nums == 1)[0]

    def __toSigned32(self, n):
        n = n & 0xffffffff
        return n | (-(n & 0x80000000))

    @staticmethod
    @nb.njit(nb.int32[::1](nb.types.Array(nb.uint8, 1, 'C', readonly=True)))
    def compute(arr):
        """
            This method is not of my own design, but is the fastest possible way that I know of (without writing my own
            C-based extension) to convert a long delimited string into a list of ints. I found this solution at
            https://stackoverflow.com/questions/74873414/the-fastest-way-possible-to-split-a-long-string

            Due to this method being 'pre-compiled' by the numba just-in-time compiler, it cannot be debugged unless the
            @nb.njit decorator line is commented out. This will cause a very noticable performance degradation, but will
            allow for the placement of breakpoints in this method for debugging.
        """
        count = len(arr)
        res = np.empty(count, np.int32)
        base = ord('0')
        val = 0
        cur = 0
        for c in arr:
            val = (val * 10) + c - base
            res[cur] = val
            cur += 1
            val = 0
        return res
