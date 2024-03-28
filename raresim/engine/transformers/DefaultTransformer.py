from raresim.engine import RunConfig
from raresim.common.sparse import SparseMatrix
from raresim.common.legend import Legend
from heapq import merge
import random


class DefaultTransformer:
    def __init__(self, runConfig: RunConfig, bins, legend: Legend, matrix: SparseMatrix):
        self.__runConfig = runConfig
        self.__bins = bins
        self.__legend = legend
        self.__matrix = matrix

    def run(self):
        bin_h = self.assign_bins()

        print('Input allele frequency distribution:')
        self.print_frequency_distribution(bin_h)

        R = []
        self.prune_bins(bin_h, R)

        print('\nNew allele frequency distribution:')
        self.print_frequency_distribution(bin_h)

        rows_to_keep = self.get_all_kept_rows(bin_h, R)
        rows_to_remove = [x for x in range(self.__matrix.num_rows()) if x not in rows_to_keep]

        for rowId in rows_to_remove[::-1]:
            self.__legend.remove_row(rowId)
            self.__matrix.remove_row(rowId)

    def prune_bins(self, bin_h, R):
        # This method is inherited by other transformers. Please ensure proper testing is done when making changes here.
        for bin_id in reversed(range(len(bin_h))):

            # The last bin contains those variants with ACs
            # greater than the bin size, and we keep all of them
            if bin_id == len(self.__bins):
                continue

            need = self.__bins[bin_id][2]
            have = len(bin_h[bin_id])

            if abs(have - need) > 3:
                p_rem = 1 - float(need) / float(have)
                row_ids_to_rem = []
                for i in range(have):
                    flip = random.uniform(0, 1)
                    if flip <= p_rem:
                        row_ids_to_rem.append(bin_h[bin_id][i])
                for row_id in row_ids_to_rem:
                    R.append(row_id)
                    bin_h[bin_id].remove(row_id)
            elif have < need - 3:
                if R < need - have:
                    raise Exception('ERROR: ' + 'Current bin has ' + str(have)
                                    + ' variant(s). Model needs ' + str(need)
                                    + ' variant(s). Only ' + str(len(R)) + ' variant(s)'
                                    + ' are available')

                p_add = float(need - have) / float(len(R))

                row_ids_to_add = []
                for i in range(len(R)):
                    flip = random.uniform(0, 1)
                    if flip <= p_add:
                        row_ids_to_add.append(R[i])
                for row_id in row_ids_to_add:
                    num_to_keep = int(random.uniform(self.__bins[bin_id][0],
                                                     self.__bins[bin_id][1]))
                    num_to_rem = self.__matrix.row_num(row_id) - num_to_keep
                    # TODO: The following line might need to be placed behind an if statement that checks
                    #       for the keep_protected argument and whether or not the row is protected via the legend.
                    left = self.__matrix.prune_row(row_id, num_to_rem)
                    assert num_to_keep == left
                    bin_h[bin_id].append(row_id)
                    R.remove(row_id)

    def get_all_kept_rows(self, bin_h, R):
        all_kept_rows = []

        for bin_id in range(len(bin_h)):
            all_kept_rows += bin_h[bin_id]

        all_kept_rows.sort()

        R = sorted(R)

        if self.__runConfig.args.z:
            all_kept_rows = list(merge(all_kept_rows, R))

        if self.__runConfig.args.keep_protected:
            protected_rows = []
            for row_id in R:
                if int(self.__legend[row_id]["protected"]) == 1:
                    protected_rows.append(row_id)
            all_kept_rows = list(merge(all_kept_rows, protected_rows))

        return set(all_kept_rows)

    def assign_bins(self):
        bin_h = {}
        row_i = 0
        for row in range(self.__matrix.num_rows()):
            row_num = self.__matrix.row_num(row)

            if row_num > 0 or self.__runConfig.args.z:
                bin_id = self.get_bin(row_num)
                target_map = bin_h
                if bin_id not in target_map:
                    target_map[bin_id] = []
                target_map[bin_id].append(row_i)

            row_i += 1
        return bin_h

    def get_bin(self, val):
        for i in range(len(self.__bins)):
            if self.__bins[i][0] <= val <= self.__bins[i][1]:
                return i
        return len(self.__bins)

    def print_frequency_distribution(self, bin_h):
        self.print_bin(bin_h)

    def print_bin(self, bin_h):
        for bin_id in range(len(bin_h)):
            if bin_id < len(self.__bins):
                print('[' + str(self.__bins[bin_id][0]) + ','
                      + str(self.__bins[bin_id][1]) + ']\t'
                      + str(self.__bins[bin_id][2]) + '\t'
                      + str(len(bin_h[bin_id])))
            else:
                print('[' + str(self.__bins[bin_id - 1][1] + 1) + ', ]\t'
                      + '\t'
                      + str(len(bin_h[bin_id])))
