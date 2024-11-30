from raresim.engine import RunConfig
from raresim.common.sparse import SparseMatrix
from raresim.common.legend import Legend
from heapq import merge
import random


class DefaultTransformer:
    """
    The default transformer is where most of the heavy lifting is done on regular raresim runs. Note that other
    transformers do inherit some functions from this one so be sure that you aren't breaking any of them when you
    make modifications here. If you aren't sure if your changes to a function will break the other transformers,
    just play it safe and copy the function over to the other transformers before making changes so that they have
    their own copies of the un-modified function.
    """
    def __init__(self, runConfig: RunConfig, bins, legend: Legend, matrix: SparseMatrix):
        self.__runConfig = runConfig
        self.__bins = bins
        self.__legend = legend
        self.__matrix = matrix

    def run(self) -> None:
        """
        Runs all the data transformation operations (namely pruning)
        NOTE: This runner works via side effects. The matrix and legend objects that were originally passed
        into this object's constructor will be modified.
        @return: None
        """
        bin_assignments = self.assign_bins()

        print('Input allele frequency distribution:')
        self.print_frequency_distribution(bin_assignments)

        R = []
        self.prune_bins(bin_assignments, R)

        print('\nNew allele frequency distribution:')
        self.print_frequency_distribution(bin_assignments)

        rows_to_keep = self.get_all_kept_rows(bin_assignments, R)
        rows_to_remove = [x for x in range(self.__matrix.num_rows()) if x not in rows_to_keep]

        for rowId in rows_to_remove[::-1]:
            self.__legend.remove_row(rowId)
            self.__matrix.remove_row(rowId)

    def prune_bins(self, bin_assignments: dict, extra_rows: list, activation_threshold: int = 3, stopping_threshold: int = 3) -> None:
        """
        NOTE: This method is inherited by other transformers. Please ensure proper testing is done when making changes here.
        This function performs the pruning process on the matrix.
        @param bin_assignments: A map of bin_id -> list of rows assigned to the bin
        @param extra_rows: list of rows that were removed and never re-added
        @param stopping_threshold:
        @param activation_threshold:
        @return: None
        """
        # Loop through the bins from largest to smallest
        for bin_id in range(len(bin_assignments))[::-1]:
            # If there are any rows with too many 1s for the largest bin, they get put into an extra bin,
            # and we do not prune these alleles away
            if bin_id == len(self.__bins):
                continue

            # How many variants to we need and how many do we have
            need = self.__bins[bin_id][2]
            have = len(bin_assignments[bin_id])

            activation = min([(float(activation_threshold) / 100) * need, 10])
            stop = (float(stopping_threshold) / 100) * need

            # If we have more rows in the bin than what we need, remove some rows
            if have - need > activation:
                # Calculate the probability to remove any given row in the bin
                prob_remove = 1 - float(need) / float(have)
                row_ids_to_rem = []
                for i in range(have):
                    # If we hit our stopping threshold to stop the pruning process, then stop the pruning process
                    if have - len(row_ids_to_rem) <= need - stop:
                        break
                    flip = random.uniform(0, 1)
                    # If the row is 'chosen' for removal, remove it and add the row to the list of rows that may be used
                    # to make up for not having enough rows in later bins
                    if flip < prob_remove:
                        row_id = bin_assignments[bin_id][i]
                        # Add the ith row in the bin to the list of row ids to remove and the list of available
                        # rows to pull from if needed later on
                        row_ids_to_rem.append(row_id)
                        extra_rows.append(row_id)
                for row_id in row_ids_to_rem:
                    bin_assignments[bin_id].remove(row_id)

            # If we don't have enough rows in the current bin, pull from the list of excess rows
            elif have < need - activation:
                if len(extra_rows) < abs(need - have):
                    raise Exception(f'ERROR: Current bin has {have} variants, but the model needs {need} variants '
                                    f'and only {len(extra_rows)} excess rows are available to use and prune down '
                                    f'from larger bins.')

                # Calculate the probability to use any given row from the available list
                prob_add = float(need - have) / float(len(extra_rows))
                row_ids_to_add = []
                for i in range(len(extra_rows)):
                    flip = random.uniform(0, 1)
                    # If the current row is 'chosen' for use, we will prune it down to the desired number of variants
                    # and add it back in to the current bin and remove it from the list of available rows to pull from
                    if flip < prob_add:
                        row_id = extra_rows[i]
                        row_ids_to_add.append(row_id)
                        num_to_keep = random.randint(self.__bins[bin_id][0], self.__bins[bin_id][1])
                        num_to_rem = self.__matrix.row_num(row_id) - num_to_keep
                        self.__matrix.prune_row(row_id, num_to_rem)
                        if self.__matrix.row_num(row_id) != num_to_keep:
                            print(
                                f"WARNING: Requested to prune row {row_id} down to {num_to_keep} variants, but after "
                                f"the request the row still has {self.__matrix.row_num} variants")
                        bin_assignments[bin_id].append(row_id)
                for row_id in row_ids_to_add:
                    extra_rows.remove(row_id)

    def get_all_kept_rows(self, bin_assignments, extra_rows) -> set:
        """
        Returns all the rows that we are keeping in the matrix
        @param bin_assignments: A map of bin_id -> list of rows assigned to the bin
        @param extra_rows: list of rows that were removed and never re-added
        @return: A set of all the row_ids that are being kept
        """
        all_kept_rows = []

        for bin_id in range(len(bin_assignments)):
            all_kept_rows += bin_assignments[bin_id]

        all_kept_rows.sort()

        if self.__runConfig.args.z:
            all_kept_rows = [x for x in range(self.__matrix.num_rows())]

        if self.__runConfig.args.keep_protected:
            protected_rows = []
            for row_id in sorted(extra_rows):
                if int(self.__legend[row_id]["protected"]) == 1:
                    protected_rows.append(row_id)
            all_kept_rows = set(merge(all_kept_rows, protected_rows))

        return set(all_kept_rows)

    def assign_bins(self) -> dict:
        """
        Calculates which rows belong to which bin given the matrix and the bin definitions
        @return: A map of bin_id -> list of rows assigned to the bin
        """
        bin_assignments = {}
        row_i = 0
        for row in range(self.__matrix.num_rows()):
            row_num = self.__matrix.row_num(row)

            if row_num > 0 or self.__runConfig.args.z:
                bin_id = self.get_bin(row_num)
                target_map = bin_assignments
                if bin_id not in target_map:
                    target_map[bin_id] = []
                target_map[bin_id].append(row_i)

            row_i += 1
        return bin_assignments

    def get_bin(self, val) -> int:
        """
        Gets the id of the bin that the provided value belongs to
        @param val: Value that you are requesting the bin_id for
        @return: The id of the bin that the provided value belongs to
        """
        for i in range(len(self.__bins)):
            if self.__bins[i][0] <= val <= self.__bins[i][1]:
                return i
        return len(self.__bins)

    def print_frequency_distribution(self, bin_assignments) -> None:
        """
        Prints out the frequency distributions given all the rows that are assigned to bins
        @param bin_assignments: A map of bin_id -> list of rows assigned to the bin
        @return: None
        """
        for bin_id in range(len(bin_assignments)):
            if bin_id < len(self.__bins):
                print('[' + str(self.__bins[bin_id][0]) + ','
                      + str(self.__bins[bin_id][1]) + ']\t'
                      + str(self.__bins[bin_id][2]) + '\t'
                      + str(len(bin_assignments[bin_id])))
            else:
                print('[' + str(self.__bins[bin_id - 1][1] + 1) + ', ]\t'
                      + '\t'
                      + str(len(bin_assignments[bin_id])))
