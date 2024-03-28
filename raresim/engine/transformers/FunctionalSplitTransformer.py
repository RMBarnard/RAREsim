from raresim.engine import RunConfig
from raresim.common.sparse import SparseMatrix
from raresim.common.legend import Legend
from raresim.engine.transformers import DefaultTransformer


class FunctionalSplitTransformer(DefaultTransformer.DefaultTransformer):
    def __init__(self, runConfig: RunConfig, bins, legend: Legend, matrix: SparseMatrix):
        super().__init__(runConfig, bins, legend, matrix)

        # See TODO comment in assign_bins() method to understand usage of this class var
        self.__currRow = None

    def run(self):
        bin_h = self.assign_bins()
        mode = self.__runConfig.getMode()

        print('Input allele frequency distribution:')
        self.print_frequency_distribution(bin_h)

        R = []

        # This transformer inherits the prune_bins method from DefaultTransformer
        if mode == 'func_split':
            R = {'fun': [], 'syn': []}
            self.prune_bins(bin_h['fun'], R['fun'])
            self.prune_bins(bin_h['syn'], R['syn'])
        elif mode == 'fun_only':
            self.prune_bins(bin_h['fun'], R)
        elif mode == 'syn_only':
            self.prune_bins(bin_h['syn'], R)

        print('\nNew allele frequency distribution:')
        self.print_frequency_distribution(bin_h)

        rows_to_keep = self.get_all_kept_rows(bin_h, R)
        rows_to_remove = [x for x in range(self.__matrix.num_rows()) if x not in rows_to_keep]

        for rowId in rows_to_remove[::-1]:
            self.__legend.remove_row(rowId)
            self.__matrix.remove_row(rowId)

    def get_all_kept_rows(self, bin_h, R):
        mode = self.__runConfig.getMode()
        all_kept_rows = []
        if mode == 'func_split':
            for bin_id in range(len(bin_h['fun'])):
                all_kept_rows += bin_h['fun'][bin_id]
            for bin_id in range(len(bin_h['syn'])):
                all_kept_rows += bin_h['syn'][bin_id]

        else:
            for bin_id in bin_h['fun']:
                all_kept_rows += bin_h['fun'][bin_id]
            for bin_id in bin_h['syn']:
                all_kept_rows += bin_h['syn'][bin_id]

        return set(sorted(all_kept_rows))

    def assign_bins(self):
        bin_h = {'fun': {}, 'syn': {}}

        row_i = 0
        for row in range(self.__matrix.num_rows()):
            row_num = self.__matrix.row_num(row)

            if row_num > 0 or self.__runConfig.args.z:
                # TODO: setting row_i to be a variable on the class is not a clean way of letting the get_bin()
                #       method know what legend row to look at in the case that this is a true func_split run.
                #       Low priority, but a better way of doing this could certainly be investigated.
                self.__currRow = row_i
                bin_id = self.get_bin(row_num)

                target_map = bin_h[self.__legend[row_i]['fun']]

                if bin_id not in target_map:
                    target_map[bin_id] = []

                target_map[bin_id].append(row_i)

            row_i += 1
        return bin_h

    def get_bin(self, val):
        if self.__runConfig.getMode() == 'func_split':
            bins = self.__bins[self.__legend[self.__currRow]['fun']]
        else:
            bins = self.__bins
        for i in range(len(bins)):
            if bins[i][0] <= val <= bins[i][1]:
                return i
        return len(bins)

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
