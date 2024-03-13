from rareSim import sparse 
import random
import sys
import argparse


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-i',
                        dest='input_file',
                        required=True,
                        help='Input haplotype file path')

    parser.add_argument('-o',
                        dest='output_file',
                        required=True,
                        help='Ouput sparse matrix path')

    args = parser.parse_args()

    return args

def main():
    args = get_args()
    M = sparse(args.input_file)
    M.write(args.output_file)

if __name__ == '__main__': main()

def convert():
