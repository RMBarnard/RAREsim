import os
from raresim.common.legend import Legend
from raresim.common.exceptions import IllegalArgumentException, RaresimException


class LegendReaderWriter:
    def __init__(self):
        pass

    @staticmethod
    def load_legend(filepath: str) -> Legend:
        """
        Reads and deserializes a provided legend file and returns the deserialized Legend object
        @param filepath: The file to read
        @return: A Legend object obtained from the provided file
        """
        if not os.path.isfile(filepath):
            raise IllegalArgumentException(f"No such file exists: {filepath}")

        with open(filepath, "r") as f:
            line = f.readline()
            header = line.rstrip().split()
            for key in header:
                if key not in Legend.Legend.SUPPORTED_COLUMNS:
                    raise RaresimException(f"Legend column '{key}' is not supported. Supported keys are {Legend.SUPPORTED_COLUMNS}")
            legend = Legend.Legend(header)

            line = f.readline()
            while line and line.strip() != "\n" and line.strip() != '':
                row = line.rstrip().split()
                legend.add_row(row)
                line = f.readline()
        return legend

    @staticmethod
    def write_legend(legend: Legend, filepath: str) -> None:
        """
        Writes the provided Legend object out to the provided file
        @param legend: Legend object to serialize
        @param filepath: Path to write the object to
        @return: None
        """
        with open(filepath, "w") as f:
            header_string = "\t".join(legend.get_header()) + "\n"
            f.write(header_string)
            for i in range(legend.row_count()):
                line = "\t".join(legend.get_row(i)) + "\n"
                f.write(line)
