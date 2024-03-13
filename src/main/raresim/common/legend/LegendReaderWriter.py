import os
from src.main.raresim.common.legend import Legend
from src.main.raresim.common.exceptions import IllegalArgumentException, RaresimException


class LegendReaderWriter:
    def __init__(self):
        pass

    def load_legend(self, filepath: str) -> Legend:
        if not os.path.isfile(filepath):
            raise IllegalArgumentException(f"No such file exists: {filepath}")

        with open(filepath, "r") as f:
            line = f.readline()
            header = line.rstrip().split()
            for key in header:
                if key not in Legend.supported_columns:
                    raise RaresimException(f"Legend column '{key}' is not supported. Supported keys are {Legend.supported_columns}")
            legend = Legend(header)

            line = f.readline()
            while line and line.strip() != "\n" and line.strip() != '':
                row = line.rstrip().split()
                legend.add_row(row)
                line = f.readline()
        return legend

    def write_legend(self, legend: Legend, filepath: str) -> None:
        with open(filepath, "w") as f:
            header_string = "\t".join(legend.get_header()) + "\n"
            f.write(header_string)
            for i in range(legend.row_count()):
                line = "\t".join(legend.get_row(i)) + "\n"
                f.write(line)
