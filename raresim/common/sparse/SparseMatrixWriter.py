import timeit

from raresim.common.sparse import SparseMatrix
import gzip
import array


class SparseMatrixWriter:
    def __init__(self):
        pass

    def writeToHapsFile(self, sparseMatrix: SparseMatrix, filename: str) -> None:
        """
        Writes the sparse matrix to a file of the format matching the file extension. Must be one of [.haps, .gz, .sm]
        @param sparseMatrix: input matrix
        @param filename: output file
        @return: None
        """
        writeTimer = timeit.default_timer()
        if filename.split(".")[-3:] == "gz":
            self.__writeZipped(sparseMatrix, filename)
        elif filename.split(".")[-3:] == "sm":
            self.__writeCompressed(sparseMatrix, filename)
        else:
            self.__writeUncompressed(sparseMatrix, filename)
        print(f"Writing haps file took {timeit.default_timer() - writeTimer} seconds")

    @staticmethod
    def __writeZipped(sparseMatrix: SparseMatrix, filename: str):
        """
        Writes the sparse matrix to a g-zipped format. Unzipping will yield a human-readable file
        @param sparseMatrix: input matrix
        @param filename: output file
        @return: None
        """
        with gzip.open(filename, "wb") as f:
            for i in range(sparseMatrix.num_rows()):
                row = ["0"]*sparseMatrix.num_cols()
                for j in sparseMatrix.get_row_raw(i):
                    row[j] = "1"
                line = " ".join(row) + "\n"
                f.write(line.encode())

    @staticmethod
    def __writeUncompressed(sparseMatrix: SparseMatrix, filename: str):
        """
        Writes the sparse matrix to an uncompressed human-readable format
        @param sparseMatrix: input matrix
        @param filename: output file
        @return: None
        """
        with open(filename, "w") as f:
            for i in range(sparseMatrix.num_rows()):
                row = ["0"] * sparseMatrix.num_cols()
                for j in sparseMatrix.get_row_raw(i):
                    row[j] = "1"
                line = " ".join(row) + "\n"
                f.write(line)

    @staticmethod
    def __writeCompressed(sparseMatrix: SparseMatrix, filename: str) -> None:
        """
        Writes the sparse matrix to a binary encoded file.
        The format was not written by me (I would personally choose a different format), but I did reverse engineer it
        decided to stick with it to maintain backwards compatibility with older .sm files. The format is as follows:
        First 4 bytes specify the number of rows (x) in the matrix.
        Second 4 bytes specify the number of columns in the matrix.
        The next x sets of 4 bytes each represent the number of 1s in the file up to the that row
        The remaining n sets of 4 bytes each represent a column with a one in it. The row of that one can be found by
        keeping track of which of the n sets of 4 bytes you are looking at and comparing it with the values in the lis
        from the x sets of bytes
        @param sparseMatrix: input matrix
        @param filename: output file
        @return: None
        """
        with open(filename, "wb") as f:
            f.write(int.to_bytes(sparseMatrix.num_rows(), 4, "little"))
            f.write(int.to_bytes(sparseMatrix.num_cols(), 4, "little"))
            countOnes = 0
            for i in range(sparseMatrix.num_rows()):
                countOnes += sparseMatrix.row_num(i)
                f.write(int.to_bytes(countOnes, 4, "little"))

            for i in range(sparseMatrix.num_rows()):
                row = sparseMatrix.get_row_raw(i)
                data = array.array("i", row)
                f.write(data.tobytes())
