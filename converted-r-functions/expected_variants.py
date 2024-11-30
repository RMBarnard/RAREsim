import argparse

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-N',
                        dest='n',
                        required=True,
                        help='Number of expected variants')
    parser.add_argument('--props',
                        dest='props',
                        required=True,
                        help='Provided mac bins with proportions')
    parser.add_argument('-o',
                        dest='output',
                        help='Output file to be written')

    args = parser.parse_args()

    return args

def nvariants():
    args = get_args()

    n = int(args.n)

    with open(args.output, 'w') as output:
        with open(args.props) as props:
            output.writelines("Lower\tUpper\tExpected_var\n")
            lines = props.readlines()[1:]
            for line in lines:
                line = line.split(',')
                output.writelines(f"{int(line[0])}\t{int(line[1])}\t{float(line[2])*n}\n")

if __name__ == '__main__':
    nvariants()
        
