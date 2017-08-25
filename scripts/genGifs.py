import argparse
import subprocess
import os


def create_cmd_all_final(args, f):
    cmd = ("python3 test.py -f "+args.folder+f+"/"+
           " -tc "+str(args.test_count)+
           " -np "+str(args.noops)+
           " -gn "+f+
           " -gf "+args.folder+"gifs/"
           " -d "+args.device)
    return cmd

def main(args):
    path = args.folder+"gifs"
    if not os.path.exists(path):
        os.makedirs(path)
    if args.game_folder == '' :
        for f in os.listdir(args.folder):
            if args.checkpoint == 0 :
                subprocess.call(create_cmd_all_final(args, f), shell = True)
            




def get_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-gf', default= '', type=str, help='Name of the games folder to generate. Default : all folder are generated.', dest='game_folder')
    parser.add_argument('-f', '--folder', type=str, help="Folder where is saved the logs of all games.", dest="folder", required=True)
    parser.add_argument('-tc', '--test_count', default='1', type=int, help="The amount of tests to run on the given network", dest="test_count")
    parser.add_argument('-cp', '--checkpoint', default='0', type=int, help="The checkpoint from which to run the test", dest="checkpoint")
    parser.add_argument('-np', '--noops', default=30, type=int, help="Maximum amount of no-ops to use", dest="noops")
    parser.add_argument('-d', '--device', default='/gpu:0', type=str, help="Device to be used ('/cpu:0', '/gpu:0', '/gpu:1',...)", dest="device")
    return parser


if __name__ == '__main__':
    args = get_arg_parser().parse_args()
    main(args)
