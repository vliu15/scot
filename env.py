import numpy as np
from typing import Tuple, List
from actions import ACTIONS

# Grid environment
class Grid(object):
    '''
    __func__ : default python function
    func     : external functionality
    _func    : internal functionality
    '''

    def __init__(self, height:int, width:int, gamma:float, gray_r:float, white_r:float,
                 weights=None, gray_sq:List[List[int]]=None, num_feat:int=2, start_corner=True, start_dist=None):
        ''' Initialize Grid environment '''
        # set metadata about mdp environment
        self.gamma = gamma
        self.nA = len(ACTIONS)
        self.nS = width*height
        self.actions_to_grid = {a: g for a, g in enumerate(ACTIONS)}
        self.grid_to_actions = {g: a for a, g in enumerate(ACTIONS)}

        # for now implement linear reward function weights in environment, should be associated with the agent
        if weights is None:
            self.weights = np.array([white_r, gray_r])
        else:
            self.weights = weights

        self.s_features = {s: (1, 0) for s in range(self.nS)}
        # set up board
        # randomly initialize gray squares if not passed in
        if not gray_sq:
            n_gray_sq = int(np.sqrt(width * height))
            gray_sq = list(zip(
                np.random.random_integers(0, width-1, n_gray_sq), np.random.random_integers(0, height-1, n_gray_sq)))
        print('Gray squares: {}'. format(gray_sq))

        self.board = np.full([height, width], white_r)
        for h, w in gray_sq:
            self.board[h, w] = gray_r
            self.s_features[self.grid_to_state((h, w))] = (0, 1)

        # set special positions
        # WILL WANT TO MAKE END STATE A SAMPLE FROM A DISTRIBUTION OF END STATES
        self.end = self.nS - 1

        # initialize start state either in upper-left grid corner or with sample from start state distribution
        # uniformly sample over all states but terminal state if no distribution is input
        if start_corner is True:
            self.start = self.grid_to_state((0, 0))
            self.start_dist = None
        elif start_dist is None:
            self.start_dist = np.array([1/(self.nS-1) for _ in range(self.nS-1)])
            self.start = (np.cumsum(self.start_dist) > np.random.random()).argmax()
        else:
            self.start_dist = start_dist
            self.start = (np.cumsum(start_dist) > np.random.random()).argmax()

        self.agent = self.start
        self.t = 0
        self.r = 0

        # logging
        self.log = [self.state_to_grid(self.agent)]
        self.traj = []

    # WILL NEED TO ADD FUNCTIONALITY FOR STOCHASTIC TRANSITIONS, MAY WANT TO JUST DIRECTLY MAP STATES AND
    # ACTIONS TO DISTRIBUTIONS OVER SUCCESSORS IN A NESTED DICTIONARY

    #- external functions -#
    def step(self, a: int):
        ''' Makes one time step in the environment '''
        s = self.agent
        new_pos = self._update_pos(self.state_to_grid(s), self.actions_to_grid[a])
        successor = self.grid_to_state(new_pos)
        # update position if action would not take the agent off the grid
        if new_pos[0] < self.board.shape[0] and new_pos[1] < self.board.shape[1] and new_pos[0] >= 0 and \
                new_pos[1] >= 0:
            # update agent position
            self.agent = successor

        r = self.reward(self.agent)
        self.log.append(self.state_to_grid(self.agent))
        self.r = self.gamma * self.r + r
        self.t += 1
        self.traj.append((s, a, r, self.agent))

        return self.agent, r, self._is_terminal()

    def reward(self, s):
        return np.dot(self.s_features[s], self.weights)

    def reset(self):
        ''' Reset environment to initial state '''
        self.t = 0
        self.r = 0

        if self.start_dist is None:
            self.start = self.grid_to_state((0, 0))
        else:
            self.start = (np.cumsum(self.start_dist) > np.random.random()).argmax()

        self.agent = self.start
        self.log = [self.state_to_grid(self.agent)]
        self.traj = []
        return self.agent

    def state_to_grid(self, s):
        return s // self.board.shape[1], s % self.board.shape[1]

    def grid_to_state(self, g):
        return g[0] * self.board.shape[1] + g[1]

    @property
    def state(self):
        ''' Returns the state of the environment '''
        return self.board, self.agent, self.t, self.r

    #- internal functions -#
    def _update_pos(self, pos, action_grid):
        ''' Calculates updated position '''
        return pos[0] + action_grid[0], pos[1] + action_grid[1]

    def _is_terminal(self):
        ''' Whether the agent has reached the terminal state '''
        return self.agent == self.end #or self.t > 5
