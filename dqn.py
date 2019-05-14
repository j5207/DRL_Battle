import tensorflow as tf
import numpy as np

# def weight_variable(shape):
#         initial = tf.truncated_normal(shape, stddev = 0.01)
#         return tf.Variable(initial)

# def bias_variable(shape):
#         initial = tf.constant(0.01, shape = shape)
#         return tf.Variable(initial)

class DuelingDQN():
    def __init__(
            self,
            n_actions,
            n_observation,
            learning_rate=0.001,
            reward_decay=0.9,
            e_greedy=0.9,
            replace_target_iter=50,
            memory_size=100,
            batch_size=32,
            e_greedy_increment=None,
            output_graph=False,
            dueling=True,
            sess=None):
#------------HYPERPARAMETER------------
        self.n_actions = n_actions
        self.n_observation = n_observation
        self.lr = learning_rate
        self.gamma = reward_decay
        self.epsilon_max = e_greedy
        self.replace_target_iter = replace_target_iter
        self.memory_size = memory_size
        self.batch_size = batch_size
        self.epsilon_increment = e_greedy_increment
        self.epsilon = 0 if e_greedy_increment is not None else self.epsilon_max

        self.dueling = dueling      # decide to use dueling DQN or not

        self.learn_step_counter = 0

        # self.state = tf.placeholder(tf.float32, shape=[None, self.NUM_OBSERVATION])
        # self.readout = None

        self.memory = np.zeros((self.memory_size, n_observation*2 + 2))
        self._build_net()
        t_params = tf.get_collection('target_net_params')
        e_params = tf.get_collection('eval_net_params')
        self.replace_target_op = [tf.assign(t, e) for t, e in zip(t_params, e_params)]

        if sess is None:
            self.sess = tf.Session()
            self.sess.run(tf.global_variables_initializer())
        else:
            self.sess = sess
        if output_graph:
            tf.summary.FileWriter("logs/", self.sess.graph)
        self.cost_his = []

#------------Building Network--------------
    def _build_net(self):
        def build_layers(s, c_names, n_l1, w_initializer, b_initializer):
            with tf.variable_scope('l1'):
                w1 = tf.get_variable('w1', [self.n_observation, 1000], initializer=w_initializer, collections=c_names)
                b1 = tf.get_variable('b1', [1, 1000], initializer=b_initializer, collections=c_names)
                l1 = tf.nn.dropout(tf.nn.relu(tf.matmul(s, w1) + b1), keep_prob=0.5)

                w2 = tf.get_variable('w2', [1000, 1000], initializer=w_initializer, collections=c_names)
                b2 = tf.get_variable('b2', [1, 1000], initializer=b_initializer, collections=c_names)
                l2 = tf.nn.dropout(tf.nn.relu(tf.matmul(l1, w2) + b2), keep_prob=0.5)

                w3 = tf.get_variable('w3', [1000, 1000], initializer=w_initializer, collections=c_names)
                b3 = tf.get_variable('b3', [1, 1000], initializer=b_initializer, collections=c_names)
                l3 = tf.nn.dropout(tf.nn.relu(tf.matmul(l2, w3) + b3), keep_prob=0.5)

                w4 = tf.get_variable('w4', [1000, 500], initializer=w_initializer, collections=c_names)
                b4 = tf.get_variable('b4', [1, 500], initializer=b_initializer, collections=c_names)
                l4 = tf.nn.dropout(tf.nn.relu(tf.matmul(l3, w4) + b4), keep_prob=0.5)

                w5 = tf.get_variable('w5', [500, n_l1], initializer=w_initializer, collections=c_names)
                b5 = tf.get_variable('b5', [1, n_l1], initializer=b_initializer, collections=c_names)
                l5 = tf.nn.dropout(tf.nn.relu(tf.matmul(l4, w5) + b5), keep_prob=0.5)

            if self.dueling:
                # Dueling DQN
                with tf.variable_scope('Value'):
                    w6 = tf.get_variable('w6', [n_l1, 1], initializer=w_initializer, collections=c_names)
                    b6 = tf.get_variable('b6', [1, 1], initializer=b_initializer, collections=c_names)
                    self.V = tf.matmul(l5, w6) + b6

                with tf.variable_scope('Advantage'):
                    w6 = tf.get_variable('w6', [n_l1, self.n_actions], initializer=w_initializer, collections=c_names)
                    b6 = tf.get_variable('b6', [1, self.n_actions], initializer=b_initializer, collections=c_names)
                    self.A = tf.nn.softmax(tf.matmul(l5, w6) + b6)

                with tf.variable_scope('Q'):
                    out = self.V + (self.A - tf.reduce_mean(self.A, axis=1, keep_dims=True))     # Q = V(s) + A(s,a)
            else:
                with tf.variable_scope('Q'):
                    w6 = tf.get_variable('w6', [n_l1, self.n_actions], initializer=w_initializer, collections=c_names)
                    b6 = tf.get_variable('b6', [1, self.n_actions], initializer=b_initializer, collections=c_names)
                    out = tf.nn.softmax(tf.matmul(l5, w6) + b5)

            return out

        # ------------------ build evaluate_net ------------------
        self.s = tf.placeholder(tf.float32, [None, self.n_observation], name='s')  # input
        self.q_target = tf.placeholder(tf.float32, [None, self.n_actions], name='Q_target')  # for calculating loss
        with tf.variable_scope('eval_net'):
            c_names, n_l1, w_initializer, b_initializer = \
                ['eval_net_params', tf.GraphKeys.GLOBAL_VARIABLES], 20, \
                tf.random_normal_initializer(0., 0.3), tf.constant_initializer(0.1)  # config of layers

            self.q_eval = build_layers(self.s, c_names, n_l1, w_initializer, b_initializer)

        with tf.variable_scope('loss'):
            self.loss = tf.reduce_mean(tf.squared_difference(self.q_target, self.q_eval))
        with tf.variable_scope('train'):

            #could try adam in future
            self._train_op = tf.train.RMSPropOptimizer(self.lr).minimize(self.loss)

        # ------------------ build target_net ------------------
        self.s_ = tf.placeholder(tf.float32, [None, self.n_observation], name='s_')    # input
        with tf.variable_scope('target_net'):
            c_names = ['target_net_params', tf.GraphKeys.GLOBAL_VARIABLES]

            self.q_next = build_layers(self.s_, c_names, n_l1, w_initializer, b_initializer)


    def store_transition(self, s, a, r, s_):
        if not hasattr(self, 'memory_counter'):
            self.memory_counter = 0
        transition = np.hstack((s, a, r, s_))
        index = self.memory_counter % self.memory_size
        self.memory[index] = transition
        self.memory_counter += 1

    def choose_action(self, observation, n_action):
        action = np.zeros((n_action, ))
        if np.random.uniform() < self.epsilon:#:  # choosing action
            actions_value = self.sess.run(self.q_eval, feed_dict={self.s: np.reshape(observation, (-1, 4))})
            action = np.argmax(actions_value)

        else:
            action = round(np.random.randint(0, n_action))
        return action

    def learn(self):
        #---------check if replace param in target to eval--------
        if self.learn_step_counter % self.replace_target_iter == 0:
            self.sess.run(self.replace_target_op)
            print('\ntarget_params_replaced\n')
        #---------random select batch sample from memory-------
        sample_index = np.random.choice(self.memory_size, size=self.batch_size)
        batch_memory = self.memory[sample_index]

        #------forward batch saved observation to recieve action
        q_next = self.sess.run(self.q_next, feed_dict={self.s_: batch_memory[:, -self.n_observation:]}) # next
        q_eval = self.sess.run(self.q_eval, feed_dict={self.s: batch_memory[:, :self.n_observation]}) # now

        q_target = q_eval.copy()
        batch_index = np.arange(self.batch_size, dtype=np.int32)

        #---------according how we store the transition-------
        eval_act_index = batch_memory[:, self.n_observation].astype(int)
        reward = batch_memory[:, self.n_observation + 1]
        #------------calculate Q Reality------------#
        q_target[batch_index, eval_act_index] = reward + self.gamma * np.max(q_next, axis=1)
        #print(reward)

        _, self.cost = self.sess.run([self._train_op, self.loss],
                                     feed_dict={self.s: batch_memory[:, :self.n_observation],
                                                self.q_target: q_target})
        self.cost_his.append(self.cost)

        self.epsilon = self.epsilon + self.epsilon_increment if self.epsilon < self.epsilon_max else self.epsilon_max
        self.learn_step_counter += 1

