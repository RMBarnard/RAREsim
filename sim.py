from rareSim import sparse
import gzip
import sys
from header import *


def main():
    args = get_args()
    legend_header, legend = read_legend(args.input_legend)
    try:
        func_split, fun_only, syn_only = get_split(args)
    except Exception as e:
        sys.exit(str(e))

    M = sparse(None)
    M.load(args.sparse_matrix)

    if M.num_cols() < 10000 and not args.small_sample:
        sys.exit("Sample sizes less than 10,000 haplotypes not supported." + \
                 " Use --small_sample flag to override this warning." + \
                 " The recommended method to simulate less than 10,000 haplotypes " + \
                 "is to oversimulate the number of haplotypes and randomly down-sample to the desired sample size.")

    try:
        verify_legend(legend, legend_header, M, func_split, args.prob)
    except Exception as e:
        print(f"WARN: {str(e)}")
    

    if args.prob:
        all_rows = []
        for row in range(M.num_rows()):
            all_rows.append(row)
        num_rows = len(all_rows)
        step = int(num_rows/10)
        i = 0
        with gzip.open(args.output_hap, 'wb') as f:
                for row_i in all_rows:
                    
                    row = []
                    for col_i in range(M.row_num(row_i)):
                        flip = random.uniform(0, 1)
                        if legend[row_i]['prob'] == '.':
                            row.append(M.get(row_i, col_i))
                        elif flip > float(legend[row_i]['prob']):
                            row.append(M.get(row_i, col_i))
                    O = ['0'] * M.num_cols()
                    for col_i in row:
                        O[col_i] = '1'

                    s = ' '.join(O) + '\n'
                    f.write(s.encode())

                    if step != 0:
                        if (i % step == 0):
                            print('.', end='', flush=True)

                    i+=1

    else:
        rows_of_zeros = []

        if args.input_legend is None or (args.output_legend is None and args.z):
            sys.exit("Legend files not provided")

        for i in range(M.num_rows()):
            if M.row_num(i) == 0:
                rows_of_zeros.append(i)

        bins = get_expected_bins(args, func_split, fun_only, syn_only)

        bin_h = assign_bins(M, bins, legend, func_split, fun_only, syn_only)
        print('Input allele frequency distribution:')
        print_frequency_distribution(bins, bin_h, func_split, fun_only, syn_only)
        R = []

        try:
            if func_split:
                R = {'fun':[], 'syn':[]}
                prune_bins(bin_h['fun'], bins['fun'], R['fun'], M, args.activation_threshold, args.stop_threshold)
                prune_bins(bin_h['syn'], bins['syn'], R['syn'], M, args.activation_threshold, args.stop_threshold)
            elif fun_only:
                prune_bins(bin_h['fun'], bins, R, M, args.activation_threshold, args.stop_threshold)
            elif syn_only:
                prune_bins(bin_h['syn'], bins, R, M, args.activation_threshold, args.stop_threshold)
            else:
                prune_bins(bin_h, bins, R, M, args.activation_threshold, args.stop_threshold)
        except Exception as e:
            sys.exit(str(e))

        print()
        print('New allele frequency distribution:')
        print_frequency_distribution(bins, bin_h, func_split, fun_only, syn_only)

        all_kept_rows = get_all_kept_rows(bin_h, R, func_split, fun_only, syn_only, args.keep_protected, legend)
        if not args.z:
            all_kept_rows = [x for x in range(M.num_rows())]

        rows_of_zeros = set(rows_of_zeros)
        all_kept_rows = [x for x in all_kept_rows if x not in rows_of_zeros]

        # No need to write a new legend when using the z flag as we are not removing rows
        if args.z:
            print()
            print('Writing new variant legend')
            write_legend(all_kept_rows, args.input_legend, args.output_legend)

        print()
        print('Writing new haplotype file', end='', flush=True)
        write_hap(all_kept_rows, args.output_hap, M)

if __name__ == '__main__': main()