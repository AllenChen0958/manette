import numpy as np

class ExplorationPolicy:

    def __init__(self, policies_list):
        self.policies_list = policies_list
        self.choice_policy = policies_list[0]
        self.choice_param = int(policies_list[1])
        self.softmax_temp = int(policies_list[2])

    def choose_next_actions(self, network, num_actions, states, session):
        network_output_v, network_output_pi = session.run(
            [network.output_layer_v,
             network.output_layer_pi],
            feed_dict={network.input_ph: states})

            # ne pas faire sesion run si egreedy et aleat ? gain de temps ?

        if self.choice_policy == "egreedy" :
            action_indices = self.e_greedy_choose(network_output_pi)
        else :
            action_indices = self.multinomial_choose(network_output_pi)
        new_actions = np.eye(num_actions)[action_indices]

        return new_actions, network_output_v, network_output_pi

    def e_greedy_choose(self, probs):
        """Sample an action from an action probability distribution output by
        the policy network using a greedy policy"""
        action_indexes = []
        for p in probs :
            if np.random.rand(1) < self.choice_param :
                action_indexes.append(np.random.randint(0,len(p)))
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

    def compute_entropy_loss(self):
        pass

    def dropout_forward(self):
        pass

    def noisy_forward(self):
        pass

    def default_forward(self):
        pass
