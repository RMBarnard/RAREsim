import argparse
import random
import sys
import gzip



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
                        required=True,
                        help='Input variant site legend')

    parser.add_argument('-L',
                        dest='output_legend',
                        required=True,
                        help='Output variant site legend')

    parser.add_argument('-H',
                        dest='output_hap',
                        required=True,
                        help='Output compress hap file')

    args = parser.parse_args()

    return args

def prune_bins(bin_h, bins, R, M):
    for bin_id in reversed(range(len(bin_h))):

	# The last binn contains those variants with ACs 
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
                sys.exit('ERROR: ' + 'Current bin has ' + str(have) \
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
                assert  num_to_keep == left

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
    with open(legend_file_name) as f:
        for l in f:
            A = l.rstrip().split()

            if header == None:
                header = A
            else:
                legend.append( dict(zip(header,A)))

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

    if args.exp_bins is None:
        if args.exp_fun_bins is not None \
            and args.exp_syn_bins is not None:
            func_split = True
        else:
            sys.exit('If variants are split by functional/synonymous ' + \
                     'files must be provided for --functional_bins ' + \
                     'and --synonymous_bins')
    return func_split


def verify_legend(legend, legend_header, M, split):
    if split and 'fun' not in legend_header:
        sys.exit('If variants are split by functional/synonymous ' + \
                 'the legend file must have a column named "fun" ' + \
                 'that specifies "fun" or "syn" for each site')
    if M.num_rows() != len(legend):
        sys.exit('Legend and haplotype files do not match in length')



def assign_bins(M, bins, legend, func_split):
    bin_h = {}

    if func_split:
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

            target_map = bin_h

            if func_split:
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
    for l in open(input_legend):
        if row_i == len(all_kept_rows):
            break

        if header == None:
            f.write(l)
            header = True
        else:
            if file_i == all_kept_rows[row_i]:
                f.write(l)
                row_i+=1
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