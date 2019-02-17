import argparse
from wrapper import Wrapper

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-width', type=int, default=5)
    parser.add_argument('-height', type=int, default=5)
    parser.add_argument('-gamma', type=float, default=0.9)
    parser.add_argument('-gray_r', type=float, default=-10.0)
    parser.add_argument('-white_r', type=float, default=0.0)
    parser.add_argument('-term_r', type=float, default=10.0)
    parser.add_argument('-n_episodes', type=float, default=3)

    args = parser.parse_args()

    print(args)

    env_wrapper = Wrapper(args.n_episodes, args.gamma, args.width, args.height,
        args.gray_r, args.white_r, args.term_r, gray_sq=[], log=True)
    
    print("Grid environment:")
    env_wrapper.print_env()

    total_r = env_wrapper.eval_episodes()

    print("Average reward with initial stochastic policy across {} episodes: {}".format(
        args.n_episodes, sum(total_r) / float(len(total_r))))

if __name__ == "__main__":
    main()