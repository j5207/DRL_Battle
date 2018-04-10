import gym
from dqn import DuelingDQN
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from game import Game

MEMORY_SIZE = 500
ITERATION = 1000
ACTION_SPACE = 12
OBSERVATION_SPACE = 4
sess = tf.Session()
Train = False

def train(RL, Train):
    acc_r = [0]
    total_steps = 0
    observation = np.zeros((OBSERVATION_SPACE, ))
    env = Game()
    done = False
    while True:
        if done and total_steps > MEMORY_SIZE:
            env.reset()
            done = False
        action = RL.choose_action(observation, ACTION_SPACE)

        reward, observation_, done = env.frame_step(action)
        print("reward:{}\nstate:{}\ndead?:{}\naction:{}\ntrain:{}\ntotal_step:{}\n".format(reward, observation_, done, action, Train, total_steps))

        acc_r.append(reward + acc_r[-1])  # accumulated reward

        RL.store_transition(observation, action, reward, observation_)

        if total_steps > MEMORY_SIZE:
            RL.learn()
            Train = True

        if total_steps-MEMORY_SIZE > ITERATION:
            break

        observation = observation_
        total_steps += 1
    return RL.cost_his, acc_r


if __name__ == "__main__":

    with tf.variable_scope('dueling'):
        dueling_DQN = DuelingDQN(
            n_actions=ACTION_SPACE, n_observation=OBSERVATION_SPACE, memory_size=MEMORY_SIZE,
            e_greedy_increment=0.001, sess=sess, dueling=True, output_graph=True)

    sess.run(tf.global_variables_initializer())
    c_dueling, r_dueling = train(dueling_DQN, Train)

    plt.figure(1)
    plt.plot(np.array(c_dueling), c='b', label='dueling')
    plt.legend(loc='best')
    plt.ylabel('cost')
    plt.xlabel('training steps')
    plt.grid()
    plt.savefig('cost11.png')


    plt.figure(2)
    plt.plot(np.array(r_dueling), c='b', label='dueling')
    plt.legend(loc='best')
    plt.ylabel('accumulated reward')
    plt.xlabel('training steps')
    plt.grid()
    plt.savefig('reward.png')
    #plt.show()