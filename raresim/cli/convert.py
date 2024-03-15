import argparse
from raresim.common.sparse import *


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-i',
                        dest='input_file',
                        required=True,
                        help='Input haplotype file path')

    parser.add_argument('-o',
                        dest='output_file',
                        required=True,
                        help='Output sparse matrix path')

    args = parser.parse_args()

    return args


def main():
    args = get_args()
    reader = SparseMatrixReader()
    writer = SparseMatrixWriter()
    matrix = reader.loadSparseMatrix(args.input_file)
    writer.writeToHapsFile(matrix, args.output_file, "sm")

if __name__ == '__main__':
    main()
