from raresim.common.exceptions import *


class RunConfig:
    def __init__(self, args):
        self.run_type: str = self.__determine_run_type(args)
        self.keep_zeroed_rows: bool = args.z
        self.small_sample: bool = args.small_sample
        self.is_probabilistic: bool = args.prob
        self.args = args

    def __determine_run_type(self, args) -> str:
        if args.exp_bins is None and not args.prob:
            if args.exp_fun_bins is not None \
                    and args.exp_syn_bins is not None:
                return "func_split"
            elif args.fun_bins_only is not None:
                return "fun_only"
            elif args.syn_bins_only is not None:
                return "syn_only"
            else:
                return
                raise IllegalArgumentException('If variants are split by functional/synonymous ' +
                                               'files must be provided for --functional_bins ' +
                                               'and --synonymous_bins')
        elif args.keep_protected:
            return "protected_run"
        elif args.prob:
            return "probabilistic"
        else:
            return "standard"
