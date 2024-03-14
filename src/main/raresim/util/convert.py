import argparse
from src.main.raresim.common.sparse import *
import timeit


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

    start = timeit.default_timer()
    matrix = reader.loadSparseMatrix(args.input_file)
    end = timeit.default_timer()
    print(f"Time taken: {end-start}")

    start = timeit.default_timer()
    writer.writeToHapsFile(matrix, args.output_file)
    end = timeit.default_timer()
    print(f"Time taken: {end-start}")

if __name__ == '__main__':
    main()
