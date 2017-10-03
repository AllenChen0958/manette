import subprocess
import os
import argparse


def create_cmd_merge(name_list, path, game):
    output_name = path+game+"_Training.mp4"
    cmd = ("mkvmerge -o "+output_name)
    l = name_list
    l.sort()
    print(l)
    for n in l[:-1]:
        cmd += " "+path+str(n)+".mp4 \+"
    cmd += " "+path+str(l[-1])+".mp4"
    return cmd

def main(args):
    path = args.folder+"training_videos/"
    if not os.path.exists(path):
        os.makedirs(path)
    f_list = os.listdir(path)
    name_list = []
    for f in f_list :
        name_list.append(int(f[:-4]))
    print(name_list)
    cmd = create_cmd_merge(name_list, path, args.game)
    print(cmd)
    subprocess.call(cmd, shell = True)


def get_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', default= 'po', type=str, help='Name of the game to train', dest='game')
    parser.add_argument('-f', '--folder', type=str, help="Folder where is saved the logs of all games.", dest="folder", required=True)
    return parser


if __name__ == '__main__':
    args = get_arg_parser().parse_args()
    main(args)
