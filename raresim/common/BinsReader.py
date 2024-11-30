class BinsReader:
    def __init__(self):
        pass

    @staticmethod
    def loadBins(filename: str) -> list:
        """
        Reads bin definitions from the provided file and returns them as a list of tuples of (lower, upper, expected_variants)
        @param filename: File from which to read the bins
        @return: A list of tuples of (lower, upper, expected_variants)
        """
        bins = []
        with open(filename) as f:
            # Skip the first line since it is the header
            f.readline()
            line = f.readline()
            while line and line.strip() != "" and line.strip() != "\n":
                row = line.rstrip().split()
                bins.append((int(row[0]), int(row[1]), float(row[2])))
                line = f.readline()
        return bins
