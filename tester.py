from raresim.engine import RunConfig, DefaultRunner
import argparse


def parseArgs():
    parser = argparse.ArgumentParser()

    parser.add_argument('-m',
                        dest='sparse_matrix',
                        required=True,
                        help='Input sparse matrix path, can be a .haps, .sm, or .gz file')

    parser.add_argument('-b',
                        dest='exp_bins',
                        help='Input expected bin sizes')

    parser.add_argument('--functional_bins',
                        dest='exp_fun_bins',
                        help='Input expected bin sizes for functional variants')

    parser.add_argument('--synonymous_bins',
                        dest='exp_syn_bins',
                        help='Input expected bin sizes for synonymous variants')

    parser.add_argument('-l',
                        dest='input_legend',
                        help='Input variant site legend')

    parser.add_argument('-L',
                        dest='output_legend',
                        help='Output variant site legend')

    parser.add_argument('-H',
                        dest='output_hap',
                        # required=True,
                        help='Output compress hap file')

    parser.add_argument('--f_only',
                        dest='fun_bins_only',
                        help='Input expected bin sizes for only functional variants')

    parser.add_argument('--s_only',
                        dest='syn_bins_only',
                        help='Input expected bin sizes for synonymous variants only')

    parser.add_argument('-z',
                        action='store_true',
                        help='Rows of zeros are not removed')

    parser.add_argument('-prob',
                        action='store_true',
                        help='Rows are pruned allele by allele given a probability of removal')

    parser.add_argument('--small_sample',
                        action='store_true',
                        help='Override error to allow for simulation of small sample size')

    parser.add_argument('--keep_protected',
                        action='store_true',
                        help='Rows in the legend marked with a 1 in the protected column will be accounted for but not pruned')

    args = parser.parse_args()

    return args


def main():
    # reader = SparseMatrixReader()
    # writer = SparseMatrixWriter()
    # writer.writeToHapsFile(reader.loadSparseMatrix("../../../testData/ProbExample.haps"), "../../../testData/ProbExample.haps.sm", True)
    runConfig = RunConfig(parseArgs())
    runner = DefaultRunner(runConfig)
    runner.run()

if __name__ == '__main__': main()
