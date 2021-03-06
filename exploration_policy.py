import numpy as np
import tensorflow as tf
import logging

class Action :
    def __init__(self, tab_rep, i, a, r):
        self.tab_rep = tab_rep
        self.id = i
        self.repeated = False
        self.current_action = 0
        self.nb_repetitions_left = 0
        self.init_from_list(a, r)


    def __str__(self):
        return "id : "+str(self.id)+", action "+str(self.current_action)+" repeated "+str(self.nb_repetitions_left)+" times."

    def init_from_list(self, a, r):
        self.current_action = np.argmax(a)
        self.nb_repetitions_left = self.tab_rep[np.argmax(r)]
        if self.nb_repetitions_left > 0 :
            self.repeated = True

    def repeat(self):
        self.nb_repetitions_left -= 1
        if self.nb_repetitions_left == 0 :
            self.repeated = False
        return self.current_action

    def reset(self):
        self.repeated = False
        self.current_action = 0
        self.nb_repetitions_left = 0

    def is_repeated(self):
        return self.repeated


class ExplorationPolicy:

    def __init__(self, args, test = False):
        self.test = test
        self.global_step = 0

        self.egreedy_policy = args.egreedy
        self.initial_epsilon = args.epsilon
        self.epsilon = args.epsilon
        self.softmax_temp = args.softmax_temp
        self.keep_percentage = args.keep_percentage
        self.annealed = args.annealed
        self.annealing_steps = 80000000
        self.max_repetition = args.max_repetition
        self.nb_choices = args.nb_choices
        self.tab_rep = self.get_tab_repetitions()

    def get_tab_repetitions(self):
        res = [0]*self.nb_choices
        res[-1] = self.max_repetition
        if self.nb_choices > 2 :
            for i in range(1, self.nb_choices-1):
                res[i] = int(self.max_repetition/(self.nb_choices-1)) * i
        return res

    def get_epsilon(self):
        if self.global_step <= self.annealing_steps:
            return self.initial_epsilon - (self.global_step * self.initial_epsilon / self.annealing_steps)
        else:
            return 0.0

    def choose_next_actions(self, network_output_pi, network_output_rep, num_actions):
        if self.test :
            action_indices = self.argmax_choose(network_output_pi)
            repetition_indices = self.argmax_choose(network_output_rep)
        elif self.egreedy_policy :
            action_indices = self.e_greedy_choose(network_output_pi)
            repetition_indices = self.e_greedy_choose(network_output_rep)
        else :
            action_indices = self.multinomial_choose(network_output_pi)
            repetition_indices = self.multinomial_choose(network_output_rep)

        new_actions = np.eye(num_actions)[action_indices]
        new_repetitions = np.eye(self.nb_choices)[repetition_indices]

        self.global_step += len(network_output_pi)
        if self.annealed : self.epsilon = get_epsilon()

        return new_actions, new_repetitions

    def argmax_choose(self, probs):
        """Choose the best actions"""
        action_indexes = []
        for p in probs :
            action_indexes.append(np.argmax(p))
        return action_indexes

    def e_greedy_choose(self, probs):
        """Sample an action from an action probability distribution output by
        the policy network using a greedy policy"""
        action_indexes = []
        for p in probs :
            if np.random.rand(1)[0] < self.epsilon :
                i = np.random.randint(0,len(p))
                action_indexes.append(i)
            else :
                action_indexes.append(np.argmax(p))
        return action_indexes

    def multinomial_choose(self, probs):
        """Sample an action from an action probability distribution output by
        the policy network using a multinomial law."""
        # Subtract a tiny value from probabilities in order to avoid
        # "ValueError: sum(pvals[:-1]) > 1.0" in numpy.multinomial
        probs = probs - np.finfo(np.float32).epsneg

        action_indexes = [int(np.nonzero(np.random.multinomial(1, p))[0]) for p in probs]
        return action_indexes
