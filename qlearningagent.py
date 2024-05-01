from agent import Agent
import numpy as np

class QLearningAgent(Agent):
    def __init__(self, file="qlearning.npy", isLearning=False):
        self.file = file        
        self.isLearning = isLearning
        #self.intervals = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45]
        self.distanceIntervals = np.linspace(0.0, 0.1, 10)[1:-1]
        self.actions = [-0.4, -0.2, -0.1, 0.0, 0.1, 0.2, 0.4]
        self.learningRate = 0.15 # Alpha
        self.discountFactor = 0.5 # Gamma
        self.explorationRate = 0.2 # Epsilon
        self.decayRate = 0.995
        self.state = None
        self.choice = None

        try:
            self.qtable = np.load(file)
        except:
            self.qtable = np.zeros(
                (len(self.distanceIntervals) + 1, 
                 len(self.distanceIntervals) + 1, 
                 len(self.distanceIntervals) + 1,
                 len(self.actions)))
            np.save(file, self.qtable)

    def getState(self, track):
        left = np.digitize(np.min(track[:9]), self.distanceIntervals)
        middle = np.digitize(0.5 * track[9], self.distanceIntervals)
        right = np.digitize(np.min(track[10:]), self.distanceIntervals)

        return (left, middle, right)
    
    def updateTable(self, state, action, reward, next_state):
        oldQvalue = self.qtable[state][action]
        maxFutureQvalue = np.max(self.qtable[next_state])
        td = reward + self.discountFactor * maxFutureQvalue
        self.qtable[state][action] = self.learningRate * (td - oldQvalue) + oldQvalue

    def action(self, observation, reward, done):
        current_state = self.getState(observation[6])

        if self.isLearning and self.state != None:
            self.updateTable(self.state, self.choice, reward, current_state)
            print("State:", self.state)
            print("Reward:", reward)
            print("Exploration Rate:", self.explorationRate)

        if self.isLearning and np.random.rand() < self.explorationRate:
            self.choice = np.random.choice(len(self.actions))
        else:
            self.choice = np.argmax(self.qtable[current_state])

        if done:
            if np.count_nonzero(self.state) < 3:
                self.updateTable(self.state, self.choice, -1000, current_state)
            np.save(self.file, self.qtable)
            self.explorationRate *= self.decayRate
            self.state = None
        else:
            self.state = current_state

        throttle = np.clip(np.average(observation[6][9]) * 5, 0.0, 1.0)

        return (self.actions[self.choice], throttle)