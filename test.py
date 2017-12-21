import os
from train import get_network_and_environment_creator
import logger_utils
import argparse
import numpy as np
import time
import tensorflow as tf
import random
from paac import PAACLearner
from exploration_policy import ExplorationPolicy, Action

def get_save_frame(name):
    import imageio
    writer = imageio.get_writer(name + '.gif', fps=30)

    def get_frame(frame):
        writer.append_data(frame)

    return get_frame

def update_memory(memory, states):
    memory[:, :-1, :, :, :] = memory[:, 1:, :, :, :]
    memory[:, -1, :, :, :] = states
    return memory


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder', type=str, help="Folder where to save the debugging information.", dest="folder", required=True)
    parser.add_argument('-tc', '--test_count', default='1', type=int, help="The amount of tests to run on the given network", dest="test_count")
    parser.add_argument('-np', '--noops', default=30, type=int, help="Maximum amount of no-ops to use", dest="noops")
    parser.add_argument('-gn', '--gif_name', default=None, type=str, help="If provided, a gif will be produced and stored with this name", dest="gif_name")
    parser.add_argument('-gf', '--gif_folder', default='', type=str, help="The folder where to save gifs.", dest="gif_folder")
    parser.add_argument('-d', '--device', default='/gpu:0', type=str, help="Device to be used ('/cpu:0', '/gpu:0', '/gpu:1',...)", dest="device")

    args = parser.parse_args()
    arg_file = os.path.join(args.folder, 'args.json')
    device = args.device
    for k, v in logger_utils.load_args(arg_file).items():
        setattr(args, k, v)
    args.max_global_steps = 0
    df = args.folder
    args.debugging_folder = '/tmp/logs'
    args.device = device

    args.random_start = False
    args.single_life_episodes = False
    if args.gif_name:
        args.visualize = 1

    args.actor_id = 0
    rng = np.random.RandomState(int(time.time()))
    args.random_seed = rng.randint(1000)

    explo_policy = ExplorationPolicy(args, test = False)
    network_creator, env_creator = get_network_and_environment_creator(args, explo_policy)
    network = network_creator()
    saver = tf.train.Saver()

    rewards = []
    environments = [env_creator.create_environment(i) for i in range(args.test_count)]
    if args.gif_name:
        for i, environment in enumerate(environments):
            environment.on_new_frame = get_save_frame(os.path.join(args.gif_folder, args.gif_name + str(i)))

    config = tf.ConfigProto(allow_soft_placement = True)
    if 'gpu' in args.device:
        config.gpu_options.allow_growth = True

    with tf.Session(config=config) as sess:
        checkpoints_ = os.path.join(df, 'checkpoints')
        network.init(checkpoints_, saver, sess)
        states = np.asarray([environment.get_initial_state() for environment in environments])
        
        if args.noops != 0:
            for i, environment in enumerate(environments):
                for _ in range(random.randint(0, args.noops)):
                    state, _, _ = environment.next(0)
                    states[i] = state
        if args.arch == 'LSTM':
            n_steps = 5
            memory = np.zeros(([args.test_count, n_steps]+list(states.shape)[1:]), dtype=np.uint8)
            for e in range(args.test_count):
                memory[e, -1, :, :, :] = states[e]
            
        episodes_over = np.zeros(args.test_count, dtype=np.bool)
        rewards = np.zeros(args.test_count, dtype=np.float32)
        while not all(episodes_over):
            if args.arch == 'LSTM' :
                readouts_pi_t, readouts_rep_t = sess.run(
                    [network.output_layer_pi, network.output_layer_rep],
                    feed_dict={network.memory_ph: memory})
            else :
                readouts_pi_t, readouts_rep_t = sess.run(
                    [network.output_layer_pi, network.output_layer_rep],
                    feed_dict={network.input_ph: states})
            actions, repetitions = explo_policy.choose_next_actions(readouts_pi_t, readouts_rep_t, env_creator.num_actions)
            for j, environment in enumerate(environments):
                macro_action = Action(explo_policy.tab_rep, j, actions[j], repetitions[j])
                state, r, episode_over = environment.next(macro_action.current_action)
                states[j] = state
                rewards[j] += r
                episodes_over[j] = episode_over
                while macro_action.is_repeated() and not episode_over :
                    state, r, episode_over = environment.next(macro_action.repeat())
                    states[j] = state
                    rewards[j] += r
                    episodes_over[j] = episode_over
                macro_action.reset()
            memory = update_memory(memory, states)

        print('Performed {} tests for {}.'.format(args.test_count, args.game))
        print('Mean: {0:.2f}'.format(np.mean(rewards)))
        print('Min: {0:.2f}'.format(np.min(rewards)))
        print('Max: {0:.2f}'.format(np.max(rewards)))
        print('Std: {0:.2f}'.format(np.std(rewards)))
