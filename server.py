#!/bin/env python

# stdin, stdout, stderr
import sys
import numpy as np
import argparse
import logging
# Global logger
logger = logging.getLogger(__name__)

def set_up_logging():
    # create console handler and set level
    ch = logging.StreamHandler()
    # create formatter
    formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(funcName)s: %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)

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
# Map indicators:
# #    - wall
# +    - force field
# A-D  - players
# 0-25 - bombs (ticks left)

class Map(object):
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.map = np.empty((self.height, self.width))
        
    def read_map(self, inpipe):
		for line_n in range(0, self.height):
            line = inpipe.readline()
			for col_n in range(0, line.size):
                map[line_n, col_n] = line[col_n]
        
    def __str__(self):
        return 'Current map=\n%s' % (repr(self.map),)

class Server(object):
    def __init__(self):
        self.players = list()
        self.bombs = list()
        self.width = 0
        self.height = 0
        self.map = None

    def read_settings(self, inpipe):
        # read dimensions
        for var in ('number_of_players', 'max_number_of_turns', 'width', 'height'):
            line = inpipe.readline().split()
            setattr(self, var, int(line[0]))
        self.map = Map(height, width)
        self.map.read_map()
        self.create_players()

class ServerApp(object):
    def set_log_level(self, loglevel):
        numeric_level = getattr(logging, loglevel.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % loglevel)
        # set log level
        logger.setLevel(numeric_level)

    def parse_args(self):
        parser = argparse.ArgumentParser(description='AI server, BombAI competition. (C) Joakim Gebart, Dan Rosenqvist 2013')
        parser.add_argument('--loglevel', choices=('CRITICAL', 'ERROR', 'WARN', 'INFO', 'DEBUG'),
                            dest='loglevel', action='store', default='INFO',
                            help='Log level (default: INFO)')
        self.args = parser.parse_args()
        self.set_log_level(self.args.loglevel)

    def run(self):
        logger.info('Starting...')
        self.parse_args()

        logger.debug('Instantiating server...')
        self.server = Server()

        logger.debug('Reading server settings...')
        self.server.read_settings(sys.stdin)

if __name__ == '__main__':
    set_up_logging()
    app = ServerApp()
    app.run()
