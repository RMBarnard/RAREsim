from src.main.raresim.common.sparse import SparseMatrix
import gzip
import array


class SparseMatrixWriter:
    def __init__(self):
        pass

    def writeToHapsFile(self, sparseMatrix: SparseMatrix, filename: str, compression="gz") -> None:
        if compression == "gz":
            self.__writeZipped(sparseMatrix, filename)
        elif compression == "sm":
            self.__writeCompressed(sparseMatrix, filename)
        else:
            self.__writeUncompressed(sparseMatrix, filename)

    def __writeZipped(self, sparseMatrix: SparseMatrix, filename: str):
        with gzip.open(filename, "wb") as f:
            for i in range(sparseMatrix.num_rows()):
                row = sparseMatrix.get_row(i)
                row = [str(x) for x in row]
                line = " ".join(row) + "\n"
                f.write(line.encode())

    def __writeUncompressed(self, sparseMatrix: SparseMatrix, filename: str):
        with open(filename, "w") as f:
            for i in range(sparseMatrix.num_rows()):
                row = sparseMatrix.get_row(i)
                row = [str(x) for x in row]
                line = " ".join(row) + "\n"
                f.write(line)

    def __writeCompressed(self, sparseMatrix: SparseMatrix, filename: str):
        with open(filename, "wb") as f:
            f.write(int.to_bytes(sparseMatrix.num_cols(), 4, "little"))
            for i in range(sparseMatrix.num_rows()):
                row = sparseMatrix.get_row_raw(i)
                data = array.array("i", row + [-1])
                f.write(data.tobytes())
