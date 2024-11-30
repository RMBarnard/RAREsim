import argparse
from raresim.common.sparse import SparseMatrixReader, SparseMatrixWriter


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-i',
                        dest='input_file',
                        required=True,
                        help='Input haplotype file path')

    parser.add_argument('-o',
                        dest='output_file',
                        required=True,
                        help='Output haplotype file path. Format will be specified by file extension. Use one of ['
                             '.sm, .gz, .haps]')

    args = parser.parse_args()

    return args


def main():
    args = get_args()
    reader = SparseMatrixReader()
    writer = SparseMatrixWriter()
    matrix = reader.loadSparseMatrix(args.input_file)
    writer.writeToHapsFile(matrix, args.output_file)


if __name__ == '__main__':
    main()
