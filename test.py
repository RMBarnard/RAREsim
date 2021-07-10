from rareSim import sparse
import random
inps = "lib/raresim/test/data/Simulated_80k_9.controls.haps"

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
	M = sparse(inps)
	for row in range( M.rcount()):
		if (M.row_not_null(row)==1):
			flip = random.uniform(0, 1)
			if flip<= 0.3:
				M.remove_row(row)
			elif flip <= 0.6:
				M.prune_row(row, 2)

	M.write('out.haps.dat')
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
