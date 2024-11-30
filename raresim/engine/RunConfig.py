from raresim.common.exceptions import *


class RunConfig:
    """
    The RunConfig class represents an object that can be passed around that has all the important config data that
    affects how we perform operations on any given run
    """
    def __init__(self, args):
        self.run_type: str = self.__determine_run_type(args)
        self.keep_zeroed_rows: bool = args.z
        self.small_sample: bool = args.small_sample
        self.is_probabilistic: bool = args.prob
        self.args = args

    @staticmethod
    def __determine_run_type(args) -> str:
        """
        Calculates the type of run we are doing based on the given arguments
        @param args: Cli arguments from the program
        @return: String representing the run type
        """
        if args.exp_bins is None and not args.prob:
            if args.exp_fun_bins is not None \
                    and args.exp_syn_bins is not None:
                return "func_split"
            elif args.fun_bins_only is not None:
                return "fun_only"
            elif args.syn_bins_only is not None:
                return "syn_only"
            else:
                raise IllegalArgumentException('If variants are split by functional/synonymous ' +
                                               'files must be provided for --functional_bins ' +
                                               'and --synonymous_bins')
        elif args.prob:
            return "probabilistic"
        else:
            return "standard"
