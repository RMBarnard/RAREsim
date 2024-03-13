from src.main.sparseMatrixLib.SparseMatrixReader import SparseMatrixReader
from src.main.sparseMatrixLib.SparseMatrixWriter import SparseMatrixWriter

reader = SparseMatrixReader()
matrix = reader.loadSparseMatrix("../../Simulated_80k_9.controls.haps")
#matrix2 = reader.loadSparseMatrix("../../test.hap.sm")
writer = SparseMatrixWriter()
writer.writeToSmFile(matrix, "../../test.hap.sm", True)