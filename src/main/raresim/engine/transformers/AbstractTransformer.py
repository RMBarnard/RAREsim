from src.main.raresim.engine import RunConfig
from src.main.raresim.common.sparse import SparseMatrix
from src.main.raresim.common.legend import Legend
import random


class AbstractTransformer:
    def __init__(self, runConfig: RunConfig):
        self.runConfig = runConfig

    def run(self, bins, legend: Legend, matrix: SparseMatrix):
        # Each individual transformer will implement this method for itself.
        raise NotImplementedError("Attempted to go down unsupported code path of abstract transformer. This should not happen")

    def get_all_kept_rows(bin_h, R, func_split, fun_only, syn_only, z, keep_protected, legend):
        # Each individual transformer will implement this method for itself.
        raise NotImplementedError("Attempted to go down unsupported code path of abstract transformer. This should not happen")

    def assign_bins(self, bins, legend: Legend, matrix: SparseMatrix) -> dict:
        bin_h = {}
        mode = self.runConfig.run_type
        if mode in ["func_split", "fun_only", "split_only"]:
            bin_h['fun'] = {}
            bin_h['syn'] = {}

        row_i = 0
        for row in range(matrix.num_rows()):
            row_num = matrix.row_num(row)

            if row_num > 0 or self.runConfig.args.z:
                if mode == "func_split":
                    bin_id = self.get_bin(bins[legend[row_i]['fun']], row_num)
                else:
                    bin_id = self.get_bin(bins, row_num)

                # Depending on split status, either append to bin_h or to just the annotated dictionary
                target_map = bin_h

                if mode in ["func_split", "fun_only", "split_only"]:
                    target_map = bin_h[legend[row_i]['fun']]

                if bin_id not in target_map:
                    target_map[bin_id] = []

                target_map[bin_id].append(row_i)

            row_i += 1
        return bin_h

    def print_frequency_distribution(self, bins, bin_h):
        mode = self.runConfig.run_type
        if mode == "func_split":
            print('Functional')
            self.print_bin(bin_h['fun'], bins['fun'])
            print('\nSynonymous')
            self.print_bin(bin_h['syn'], bins['syn'])
        elif mode == "fun_only":
            print('Functional')
            self.print_bin(bin_h['fun'], bins)
        elif mode == "syn_only":
            print('Synonymous')
            self.print_bin(bin_h['syn'], bins)
        else:
            self.print_bin(bin_h, bins)

    @staticmethod
    def print_bin(bin_h, bins):
        for bin_id in range(len(bin_h)):
            if bin_id < len(bins):
                print('[' + str(bins[bin_id][0]) + ','
                      + str(bins[bin_id][1]) + ']\t'
                      + str(bins[bin_id][2]) + '\t'
                      + str(len(bin_h[bin_id])))
            else:
                print('[' + str(bins[bin_id - 1][1] + 1) + ', ]\t'
                      + '\t'
                      + str(len(bin_h[bin_id])))

    @staticmethod
    def get_bin(bins, val):
        for i in range(len(bins)):
            if bins[i][0] <= val <= bins[i][1]:
                return i
        return len(bins)

    @staticmethod
    def prune_bins(bin_h, bins, R, M):
        for bin_id in reversed(range(len(bin_h))):

            # The last bin contains those variants with ACs
            # greater than the bin size, and we keep all of them
            if bin_id == len(bins):
                continue

            need = bins[bin_id][2]
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
                                    + ' are avaiable')

                p_add = float(need - have) / float(len(R))

                row_ids_to_add = []
                for i in range(len(R)):
                    flip = random.uniform(0, 1)
                    if flip <= p_add:
                        row_ids_to_add.append(R[i])
                for row_id in row_ids_to_add:
                    num_to_keep = int(random.uniform(bins[bin_id][0],
                                                     bins[bin_id][1]))
                    num_to_rem = M.row_num(row_id) - num_to_keep
                    left = M.prune_row(row_id, num_to_rem)
                    assert num_to_keep == left
                    bin_h[bin_id].append(row_id)
                    R.remove(row_id)
