from raresim.engine import RunConfig
from raresim.common.sparse import SparseMatrix
from raresim.common.legend import Legend
from raresim.engine.transformers import DefaultTransformer


class FunctionalSplitTransformer(DefaultTransformer.DefaultTransformer):
    """
    This transformer handles all func_split, fun_only, and syn_only data processing/transformation. It has a
    functional/synonymous split specific version bin assignment. It uses the prune_bins function from
    DefaultTransformer.py and just calls it on one of the types at a time
    """
    def __init__(self, runConfig: RunConfig, bins, legend: Legend, matrix: SparseMatrix):
        super().__init__(runConfig, bins, legend, matrix)

    def run(self):
        """
        Runs all the data transformation operations that consider variant types
        NOTE: This runner works via side effects. The matrix and legend objects that were originally passed
        into this object's constructor will be modified.
        @return: None
        """
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

    def get_all_kept_rows(self, bin_assignments, extra_rows):
        """
        Returns all the rows that we are keeping in the matrix
        @param bin_assignments: A map of bin_id -> list of rows assigned to the bin
        @param extra_rows: list of rows that were removed and never re-added
        @return: A set of all the row_ids that are being kept
        """
        mode = self.__runConfig.getMode()
        all_kept_rows = []
        if mode == 'func_split':
            for bin_id in range(len(bin_assignments['fun'])):
                all_kept_rows += bin_assignments['fun'][bin_id]
            for bin_id in range(len(bin_assignments['syn'])):
                all_kept_rows += bin_assignments['syn'][bin_id]

        else:
            for bin_id in bin_assignments['fun']:
                all_kept_rows += bin_assignments['fun'][bin_id]
            for bin_id in bin_assignments['syn']:
                all_kept_rows += bin_assignments['syn'][bin_id]

        return set(sorted(all_kept_rows))

    def assign_bins(self) -> dict:
        """
        Calculates which rows belong to which bin given the matrix and the bin definitions. This override of the
        inherited method takes into account the variant type of each row
        @return: A map of bin_id -> variantType -> rows assigned to the bin/variantType
        """
        bin_assignments = {'fun': {}, 'syn': {}}

        row_i = 0
        for row in range(self.__matrix.num_rows()):
            row_num = self.__matrix.row_num(row)

            if row_num > 0 or self.__runConfig.args.z:
                bin_id = self.get_bin_func(row_num, row_i)

                target_map = bin_assignments[self.__legend[row_i]['fun']]

                if bin_id not in target_map:
                    target_map[bin_id] = []

                target_map[bin_id].append(row_i)

            row_i += 1
        return bin_assignments

    def get_bin_func(self, val: int, current_row: int) -> int:
        """
        Gets the id of the bin that the provided value belongs to
        @param val: Value that you are requesting the bin_id for (to know if it is a functional or synonymous row)
        @param current_row: id of the row that we are requesting a bin for
        @return: The id of the bin that the provided value belongs to
        """
        if self.__runConfig.getMode() == 'func_split':
            bins = self.__bins[self.__legend[self.__currRow]['fun']]
        else:
            bins = self.__bins
        for i in range(len(bins)):
            if bins[i][0] <= val <= bins[i][1]:
                return i
        return len(bins)
