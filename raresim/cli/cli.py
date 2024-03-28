from raresim.common.sparse import SparseMatrixReader, SparseMatrixWriter
from raresim.engine import RunConfig, DefaultRunner
import argparse


def parseCommand():
    parser = argparse.ArgumentParser()

    parser.add_argument("command",
                        choices=['sim', 'convert']
                        )
    parser.add_argument('-i',
                        dest='input_file',
                        help='Input haplotype file path for convert functionality')

    parser.add_argument('-o',
                        dest='output_file',
                        help='Output sparse matrix path for convert functionality')

    parser.add_argument('-m',
                        dest='sparse_matrix',
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
                        help='Rows in the legend marked with a 1 in the protected column will be accounted'
                             ' for but not pruned')

    args = parser.parse_args()
    print("1")

    return args


# def parseConvertArgs():
#     parser = argparse.ArgumentParser()
#
#     parser.add_argument('-i',
#                         dest='input_file',
#                         required=True,
#                         help='Input haplotype file path')
#
#     parser.add_argument('-o',
#                         dest='output_file',
#                         required=True,
#                         help='Output sparse matrix path')
#
#     args = parser.parse_args()
#
#     print("2")
#     return args
#
#
# def parseSimArgs():
#     parser = argparse.ArgumentParser()
#
#     parser.add_argument('-m',
#                         dest='sparse_matrix',
#                         required=True,
#                         help='Input sparse matrix path, can be a .haps, .sm, or .gz file')
#
#     parser.add_argument('-b',
#                         dest='exp_bins',
#                         help='Input expected bin sizes')
#
#     parser.add_argument('--functional_bins',
#                         dest='exp_fun_bins',
#                         help='Input expected bin sizes for functional variants')
#
#     parser.add_argument('--synonymous_bins',
#                         dest='exp_syn_bins',
#                         help='Input expected bin sizes for synonymous variants')
#
#     parser.add_argument('-l',
#                         dest='input_legend',
#                         help='Input variant site legend')
#
#     parser.add_argument('-L',
#                         dest='output_legend',
#                         help='Output variant site legend')
#
#     parser.add_argument('-H',
#                         dest='output_hap',
#                         help='Output compress hap file')
#
#     parser.add_argument('--f_only',
#                         dest='fun_bins_only',
#                         help='Input expected bin sizes for only functional variants')
#
#     parser.add_argument('--s_only',
#                         dest='syn_bins_only',
#                         help='Input expected bin sizes for synonymous variants only')
#
#     parser.add_argument('-z',
#                         action='store_true',
#                         help='Rows of zeros are not removed')
#
#     parser.add_argument('-prob',
#                         action='store_true',
#                         help='Rows are pruned allele by allele given a probability of removal')
#
#     parser.add_argument('--small_sample',
#                         action='store_true',
#                         help='Override error to allow for simulation of small sample size')
#
#     parser.add_argument('--keep_protected',
#                         action='store_true',
#                         help='Rows in the legend marked with a 1 in the protected column will be accounted'
#                              ' for but not pruned')
#
#     args = parser.parse_args()
#     print("3")
#
#     return args


def main():
    command = parseCommand()
    if command.command == 'sim':
        runConfig = RunConfig(command)
        runner = DefaultRunner(runConfig)
        runner.run()

    elif command.command == 'convert':
        args = command
        reader = SparseMatrixReader.SparseMatrixReader()
        writer = SparseMatrixWriter.SparseMatrixWriter()
        matrix = reader.loadSparseMatrix(args.input_file)
        writer.writeToHapsFile(matrix, args.output_file, "sm")


if __name__ == '__main__':
    main()
