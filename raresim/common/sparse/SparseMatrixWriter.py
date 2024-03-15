import timeit

from raresim.common.sparse import SparseMatrix
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
        """
        Writes the sparse matrix to a g-zipped format. Unzipping will yield a human-readable file
        @param sparseMatrix: input matrix
        @param filename: output file
        @return: None
        """
        with gzip.open(filename, "wb") as f:
            print(sparseMatrix.num_rows())
            start = timeit.default_timer()
            for i in range(sparseMatrix.num_rows()):
                row = ["0"]*sparseMatrix.num_cols()
                for j in sparseMatrix.get_row_raw(i):
                    row[j] = "1"
                line = " ".join(row) + "\n"
                f.write(line.encode())
                if i % 1000 == 0:
                    print(timeit.default_timer() - start)
                    start = timeit.default_timer()

    def __writeUncompressed(self, sparseMatrix: SparseMatrix, filename: str):
        """
        Writes the sparse matrix to an uncompressed human-readable format
        @param sparseMatrix: input matrix
        @param filename: output file
        @return: None
        """
        with open(filename, "w") as f:
            for i in range(sparseMatrix.num_rows()):
                row = sparseMatrix.get_row(i)
                row = [str(x) for x in row]
                line = " ".join(row) + "\n"
                f.write(line)

    def __writeCompressed(self, sparseMatrix: SparseMatrix, filename: str):
        """
        Writes the sparse matrix to a binary encoded file. Values of -1 (0xFFFFFFFF) are considered row delimiters.
        @param sparseMatrix: input matrix
        @param filename: output file
        @return: None
        """
        with open(filename, "wb") as f:
            f.write(int.to_bytes(sparseMatrix.num_cols(), 4, "little"))
            for i in range(sparseMatrix.num_rows()):
                row = sparseMatrix.get_row_raw(i)
                data = array.array("i", row + [-1])
                f.write(data.tobytes())
            # # Write the last row outside of the loop to avoid appending an extra delimiter at the end.
            # # If there were an extra delimiter it would read it in as a row of all zeros in the reader and throw off
            # # the row count of the matrix
            # last_row = array.array("i", sparseMatrix.get_row_raw(sparseMatrix.num_rows()-1))
            # f.write(last_row.tobytes())
