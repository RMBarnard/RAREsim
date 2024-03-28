from raresim.engine.transformers.DefaultTransformer import DefaultTransformer
from raresim.common.legend import Legend
from raresim.common.sparse import SparseMatrix
from raresim.engine import RunConfig
import random


class StandardTransformer(DefaultTransformer):
    def __init__(self, runConfig: RunConfig, legend: Legend, matrix: SparseMatrix):
        super().__init__(runConfig, None, legend, matrix)

    def run(self):
        for row_index in range(len(self.__matrix.num_rows())):
            row = self.__matrix.get_row_raw(row_index)
            for col_index in row:
                flip = random.uniform(0, 1)
                legend_val = self.__legend[row_index]['prob']
                if legend_val == '.':
                    continue
                elif flip > float(legend_val):
                    self.__matrix.remove(row_index, col_index)
