#!/bin/env python

# stdin, stdout, stderr
import sys
import numpy as np

class Player(object):
    def __init__(self, player_id, x, y):
        self.player_id = player_id
        self.x = x
        self.y = y

    def __str__(self):
        return 'Player %(player_id)d at (%(x)d, %(y)d)' % (self.__dict__)

    def __repr__(self):
        return 'Player(player_id=%(player_id)d, x=%(x)d, y=%(y)d)' % (self.__dict__)

class Bomb(object):
    def __init__(self, player_id, x, y, ticks):
        self.player_id = player_id
        self.x = x
        self.y = y
        self.ticks = ticks

    def __str__(self):
        return 'Bomb by player %(player_id)d at (%(x)d, %(y)d)' % (self.__dict__)

    def __repr__(self):
        return 'Bomb(player_id=%(player_id)d, x=%(x)d, y=%(y)d, ticks=%(ticks)d)' % (self.__dict__)

class Map(object):
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.map = np.empty((self.height, self.width))
        
    def read_map(self):
		for line_n in range(0, self.height):
            line = sys.stdin.readline()
			for col_n in range(0, line.size):
                map[line_n, col_n] = line[col_n]
        
    def __str__(self):
        return 'Current map=\n%s' % (repr(self.map),)

class ServerApp(object):
    def __init__(self):
        self.players = list()
        self.bombs = list()
        self.width = 0
        self.height = 0
        self.map = None

    def read_settings(self):
        # read dimensions
        for var in ('number_of_players', 'max_number_of_turns', 'width', 'height'):
            line = sys.stdin.readline().split()
            setattr(self, var, line[0])
        self.map = Map(height, width)
        self.map.read_map()

    def run(self):
        self.read_settings()




if __name__ == '__main__':
    app = ServerApp()
    app.run()
