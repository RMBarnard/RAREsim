from raresim.engine import RunConfig
from raresim.common.sparse import SparseMatrix
from raresim.common.legend import Legend
from raresim.engine.transformers import AbstractTransformer
from heapq import merge


class StandardTransformer(AbstractTransformer.AbstractTransformer):
    def __init__(self, runConfig: RunConfig):
        super().__init__(runConfig)
        self.__runConfig = runConfig

    def run(self, bins, legend: Legend, matrix: SparseMatrix):
        bin_h = self.assign_bins(bins, legend, matrix)
        print('Input allele frequency distribution:')
        self.print_frequency_distribution(bins, bin_h)

        R = []
        self.prune_bins(bin_h, bins, R, matrix)

        print()
        print('New allele frequency distribution:')
        self.print_frequency_distribution(bins, bin_h)

        rows_to_keep = self.get_all_kept_rows(bin_h, R)
        rows_to_remove = [x for x in range(matrix.num_rows()) if x not in rows_to_keep]

        for rowId in rows_to_remove[::-1]:
            legend.remove_row(rowId)
            matrix.remove_row(rowId)

    def get_all_kept_rows(self, bin_h, R):
        all_kept_rows = []

        for bin_id in range(len(bin_h)):
            all_kept_rows += bin_h[bin_id]

        all_kept_rows.sort()

        R = sorted(R)

        if self.__runConfig.args.z:
            all_kept_rows = list(merge(all_kept_rows, R))

        return set(all_kept_rows)
