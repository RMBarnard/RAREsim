import argparse
from os import SEEK_END
import random
import gzip
from heapq import merge

class Error(Exception):
    """Base class for other exceptions"""
    pass

class DifferingLengths(Error):
    """Raised when two file lengths differ"""
    pass

class MissingColumn(Error):
    """Raised when legend is missing a column"""
    pass

class MissingProbs(Error):
    """Raised when legend is missing probs column"""
    pass


def get_bin(bins, val):
    for i in range(len(bins)):
        if val >= bins[i][0] and val <= bins[i][1]:
            return i
    return i+1

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-m',
                        dest='sparse_matrix',
                        required=True,
                        help='Input sparse matrix path')

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
                        required=True,
                        help='Output compress hap file')

    parser.add_argument('--f_only',
                        dest='fun_bins_only',
                        help='Input expected bin sizes for only functional variants')

    parser.add_argument('--s_only',
                        dest='syn_bins_only',
                        help='Input expected bin sizes for synonymous variants only')

    parser.add_argument('-z',
                        action='store_true',
                        help='Rows of zeros are removed from input haps file')

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

def prune_bins(bin_h, bins, R, M):
    for bin_id in reversed(range(len(bin_h))):

	# The last bin contains those variants with ACs
	# greater than the bin size, and we keep all of them
        if bin_id == len(bins):
            continue

        need = bins[bin_id][2]
        have = len(bin_h[bin_id])

        if abs(have - need) > 3:
            p_rem = 1 - float(need)/float(have)
            row_ids_to_rem = []
            for i in range(have):
                flip = random.uniform(0, 1)
                if flip <= p_rem:
                    row_ids_to_rem.append(bin_h[bin_id][i])
            for row_id in row_ids_to_rem:
                R.append(row_id)
                bin_h[bin_id].remove(row_id)
        elif have < need - 3:
            if R < need - have:
                raise Exception('ERROR: ' + 'Current bin has ' + str(have) \
                         + ' variant(s). Model needs ' + str(need) \
                         + ' variant(s). Only ' + str(len(R)) + ' variant(s)' \
                         + ' are avaiable')

            p_add = float(need - have)/float(len(R))

            row_ids_to_add = []
            for i in range(len(R)):
                flip = random.uniform(0, 1)
                if flip <= p_add:
                    row_ids_to_add.append(R[i])
            for row_id in row_ids_to_add:
                num_to_keep = int(random.uniform(bins[bin_id][0],\
                                                 bins[bin_id][1]))
                num_to_rem = M.row_num(row_id) - num_to_keep
                left = M.prune_row(row_id, num_to_rem)
                assert num_to_keep == left
                bin_h[bin_id].append(row_id)
                R.remove(row_id)


def print_bin(bin_h, bins):
    for bin_id in range(len(bin_h)):
        if bin_id < len(bins):
            print('[' + str(bins[bin_id][0]) + ',' \
            	  + str(bins[bin_id][1]) + ']\t' \
            	  + str(bins[bin_id][2]) + '\t' \
		  + str(len(bin_h[bin_id])))
        else:
            print('[' + str(bins[bin_id-1][1]+1) + ', ]\t' \
            	  +  '\t' \
		  + str(len(bin_h[bin_id])))

def read_legend(legend_file_name):
    header = None
    legend = []
    with open(legend_file_name, "r") as f:
        for l in f:
            A = l.rstrip().split()

            if header == None:
                header = A
            else:
                legend.append(dict(zip(header,A)))

    return header, legend

def read_expected(expected_file_name):

    bins = []

    header = None
    with open(expected_file_name) as f:
        for l in f:
            A = l.rstrip().split()

            if header == None:
                header = A
            else:
                bins.append( (int(A[0]), int(A[1]), float(A[2]) ) )

    return bins



def get_split(args):
    func_split = False
    fun_only = False
    syn_only = False

    if args.exp_bins is None and not args.prob:
        if args.exp_fun_bins is not None \
            and args.exp_syn_bins is not None:
            func_split = True
        elif args.fun_bins_only is not None:
            fun_only = True
        elif args.syn_bins_only is not None:
            syn_only = True
        else:
            raise Exception('If variants are split by functional/synonymous ' + \
                     'files must be provided for --functional_bins ' + \
                     'and --synonymous_bins')
    return func_split, fun_only, syn_only

def verify_legend(legend, legend_header, M, split, probs):
    if split and 'fun' not in legend_header and not probs:
        raise MissingColumn('If variants are split by functional/synonymous ' + \
                 'the legend file must have a column named "fun" ' + \
                 'that specifies "fun" or "syn" for each site')

    if M.num_rows() != len(legend):
        raise DifferingLengths(f"Lengths of legend {len(legend)} and hap {M.num_rows()} files do not match")

    if probs and 'prob' not in legend_header:
        raise MissingProbs('The legend file needs to have a "prob" column ' + \
                'to indicate the pruning probability of a given row ')




def assign_bins(M, bins, legend, func_split, fun_only, syn_only):
    bin_h = {}

    if func_split or fun_only or syn_only:
        bin_h['fun'] = {}
        bin_h['syn'] = {}

    row_i = 0
    for row in range( M.num_rows()):
        row_num = M.row_num(row)

        if row_num > 0:
            if func_split:
                bin_id = get_bin(bins[legend[row_i]['fun']], row_num)
            else:
                bin_id = get_bin(bins, row_num)

            #Depending on split status, either append to bin_h or to just the annotated dictionary
            target_map = bin_h

            if func_split or syn_only or fun_only:
                target_map = bin_h[legend[row_i]['fun']]

            if bin_id not in target_map:
                target_map[bin_id] = []


            target_map[bin_id].append(row_i)

        row_i += 1
    return bin_h


def write_legend(all_kept_rows, input_legend, output_legend):
    header = None
    file_i = 0
    row_i = 0
    f = open(output_legend, 'w')
    r = open(f'{output_legend}-pruned-variants', 'w')
    with open(input_legend, "r") as in_file:
        for l in in_file.readlines():
            if row_i == len(all_kept_rows):
                break
    
            if header == None:
                f.write(l)
                header = True
            else:
                if file_i == all_kept_rows[row_i]:
                    f.write(l)
                    row_i+=1
                else:
                    r.write(l)
                file_i+=1


def write_hap(all_kept_rows, output_file, M):
    step = int(len(all_kept_rows)/10)
    i = 0

    with gzip.open(output_file, 'wb') as f:
        for row_i in all_kept_rows:
            row = []
            for col_i in range(M.row_num(row_i)):
                row.append(M.get(row_i, col_i))

            O = ['0'] * M.num_cols()

            for col_i in row:
                O[col_i] = '1'

            s = ' '.join(O) + '\n'
            f.write(s.encode())

            if (i % step == 0):
                print('.', end='', flush=True)


            i+=1
    print()



def print_frequency_distribution(bins, bin_h, func_split, fun_only, syn_only):
    if func_split:
        print('Functional')
        print_bin(bin_h['fun'], bins['fun'])
        print('\nSynonymous')
        print_bin(bin_h['syn'], bins['syn'])
    elif fun_only:
        print('Functional')
        print_bin(bin_h['fun'], bins)
    elif syn_only:
        print('Synonymous')
        print_bin(bin_h['syn'], bins)
    else:
        print_bin(bin_h, bins)


def get_all_kept_rows(bin_h, R, func_split, fun_only, syn_only, keep_protected, legend):
    all_kept_rows = []

    if func_split:
        for bin_id in range(len(bin_h['fun'])):
            all_kept_rows += bin_h['fun'][bin_id]
        for bin_id in range(len(bin_h['syn'])):
            all_kept_rows += bin_h['syn'][bin_id]

    elif fun_only or syn_only:
        for bin_id in bin_h['fun']:
            all_kept_rows += bin_h['fun'][bin_id]
        for bin_id in bin_h['syn']:
            all_kept_rows += bin_h['syn'][bin_id]

    else:
        for bin_id in range(len(bin_h)):
            all_kept_rows += bin_h[bin_id]

    all_kept_rows.sort()

    if isinstance(R, dict):
        R = [item for sublist in R.values() for item in sublist]
    R = sorted(R)

    if keep_protected:
        keep_rows = []
        for row_id in R:
            if int(legend[row_id]["protected"]) == 1:
                keep_rows.append(row_id)
        all_kept_rows = list(merge(all_kept_rows, keep_rows))

    all_kept_rows = list(dict.fromkeys(all_kept_rows))
    return all_kept_rows


def get_expected_bins(args, func_split, fun_only, syn_only):
    bins = None
    if func_split:
        bins = {}
        bins['fun'] = read_expected(args.exp_fun_bins)
        bins['syn'] = read_expected(args.exp_syn_bins)
    elif syn_only:
        bins = read_expected(args.syn_bins_only)
    elif fun_only:
        bins = read_expected(args.fun_bins_only)
    else:
        bins = read_expected(args.exp_bins)
    return bins