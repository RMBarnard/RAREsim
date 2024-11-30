from raresim.common.sparse import *
from raresim.common.legend import *
from raresim.engine import RunConfig
from raresim.engine.transformers import *
from raresim.common.exceptions import *
from raresim.common import BinsReader
from typing import Union
import timeit


class DefaultRunner:
    """
    The default runner handles all of the boilerplate and input validations and reading/writing of files before
    calling the appropriate Transformer for the run type to perform data transformations
    """
    def __init__(self, runConfig: RunConfig):
        self.matrix_reader = SparseMatrixReader.SparseMatrixReader()
        self.matrix_writer = SparseMatrixWriter.SparseMatrixWriter()
        self.bins_reader = BinsReader.BinsReader()
        self.legend_reader_writer = LegendReaderWriter.LegendReaderWriter()
        self.args = runConfig.args
        self.runConfig = runConfig

    def run(self) -> None:
        """
        Performs all three stages of the raresim "ETL"
        E: Extract haplotype, legend, and bin data from provided files
        T: Transform data via the pruning process based on extracted data from files
        L: Load the transformed data into output files
        @return: None
        """
        # Start our run timer
        timer = timeit.default_timer()
        # Start with loading all the necessary data
        matrix: SparseMatrix = self.matrix_reader.loadSparseMatrix(self.args.sparse_matrix)
        legend: Legend = self.legend_reader_writer.load_legend(self.args.input_legend)
        bins = self.get_bins()

        # Validate inputs
        if legend.row_count() != matrix.num_rows():
            print(f"Legend and Hap file lengths do not match. \n"
                                           f"Legend: {legend.row_count()}, Haps: {matrix.num_rows()}")

        if self.args.input_legend is None or self.args.output_legend is None:
            raise IllegalArgumentException("Legend files not provided")

        transformer = self.get_transformer(bins, legend, matrix)
        transformer.run()

        print()
        print('Writing new variant legend')
        self.legend_reader_writer.write_legend(legend, self.args.output_legend)

        print()
        print('Writing new haplotype file')
        self.matrix_writer.writeToHapsFile(matrix, self.args.output_hap)
        print(f"Total runtime is {timeit.default_timer() - timer} seconds.")

    def get_bins(self) -> Union[list, dict]:
        """
        Loads the bins for the run depending on the run type.
        @return: Either a list or a dict{variantType -> list} depending on run type
        """
        mode = self.runConfig.run_type
        bins = None
        if mode == "func_split":
            bins = {}
            bins['fun'] = self.bins_reader.loadBins(self.args.exp_fun_bins)
            bins['syn'] = self.bins_reader.loadBins(self.args.exp_syn_bins)
        elif mode == "syn_only":
            bins = self.bins_reader.loadBins(self.args.syn_bins_only)
        elif mode == "fun_only":
            bins = self.bins_reader.loadBins(self.args.fun_bins_only)
        else:
            bins = self.bins_reader.loadBins(self.args.exp_bins)
        return bins

    def get_transformer(self, bins, legend, matrix):
        """
        Gets the appropriate transformer for the given run configuration
        @param bins: bins to be passed to the eventual transformer
        @param legend: legend to be passed into the eventual transformer
        @param matrix: matrix to be passed into the eventual transformer
        @return: The appropriate transformer for the given run configuration
        """
        mode = self.runConfig.run_type
        print(f"Running with run mode: {mode}")
        if mode == "standard":
            return DefaultTransformer.DefaultTransformer(self.runConfig, bins, legend, matrix)
        if mode == "func_split":
            return FunctionalSplitTransformer(self.runConfig, ["fun", "syn"])
        if mode == "fun_only":
            return FunctionalSplitTransformer(self.runConfig, ["fun"])
        if mode == "syn_only":
            return FunctionalSplitTransformer(self.runConfig, ["syn"])
        if mode == "probabilistic":
            return ProbabilisticTransformer(self.runConfig)
