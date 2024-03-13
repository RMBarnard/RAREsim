from src.main.sparseMatrixLib.SparseMatrix import SparseMatrix
import array


class SparseMatrixWriter:
    def __init__(self):
        pass

    def writeToSmFile(self, sparseMatrix: SparseMatrix, filename: str, compress: bool) -> None:
        if compress:
            self._writeCompressed(sparseMatrix, filename)
        else:
            self._writeUncompressed(sparseMatrix, filename)

    def _writeUncompressed(self, sparseMatrix: SparseMatrix, filename: str):
        with open(filename, "w") as f:
            for i in range(sparseMatrix.num_rows()):
                row = sparseMatrix.get_row(i)
                row = [str(x) for x in row]
                line = " ".join(row)
                f.write(line + "\n")
    def _writeCompressed(self, sparseMatrix: SparseMatrix, filename: str):
        with open(filename, "wb") as f:
            f.write(int.to_bytes(sparseMatrix.num_cols(), 4, "little"))
            for i in range(sparseMatrix.num_rows()):
                row = sparseMatrix.get_row_raw(i)
                data = array.array("i", row + [-1])
                f.write(data.tobytes())
