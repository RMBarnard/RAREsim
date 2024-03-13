import os
from src.main.sparseMatrixLib.SparseMatrix import SparseMatrix
from src.main.raresimCommonLib.exceptions.IllegalArgumentException import IllegalArgumentException


class SparseMatrixReader:
    def __init__(self):
        pass

    def loadSparseMatrix(self, filepath: str) -> SparseMatrix:
        if not os.path.isfile(filepath):
            raise IllegalArgumentException(f"No such file exists: {filepath}")
        if filepath[-3:] == '.sm':
            return self._loadCompressed(filepath)
        return self._loadUncompressed(filepath)

    def _loadCompressed(self, filepath: str) -> SparseMatrix:
        with open(filepath, "rb") as f:
            data = f.read(4)
            matrix = SparseMatrix(int.from_bytes(data, "little"))
            row = []
            while data:
                if self._toSigned32(int.from_bytes(data, "little")) ==-1:
                    matrix.add_row(row)
                    row = []
                else:
                    row.append(int.from_bytes(data, "little"))
                data = f.read(4)
        return  matrix

    def _loadUncompressed(self, filepath: str) -> SparseMatrix:
        with open(filepath, "r") as f:
            line = f.readline()
            nums = line.split(" ")
            matrix = SparseMatrix(len(nums))
            matrix.add_row(self._getSparseRow(nums))
            while True:
                line = f.readline()
                if line is None or line == "":
                    break
                nums = line.split(" ")
                matrix.add_row(self._getSparseRow(nums))
        return matrix

    def _getSparseRow(self, nums: list) -> list:
        ret = []
        for i in range(len(nums)):
            if nums[i] == "1":
                ret.append(i)
        return ret

    def _toSigned32(self, n):
        n = n & 0xffffffff
        return n | (-(n & 0x80000000))