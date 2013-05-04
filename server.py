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
    MOVE_PASS  = 'pass'
    MOVE_LEFT  = 'left'
    MOVE_RIGHT = 'right'
    MOVE_UP    = 'up'
    MOVE_DOWN  = 'down'
    ALL_MOVES = (MOVE_PASS, MOVE_LEFT, MOVE_RIGHT, MOVE_UP, MOVE_DOWN)

    def __init__(self, player_id, x, y):
        self.player_id = player_id
        self.x = x
        self.y = y
        self.move = MOVE_PASS

    def __str__(self):
        return 'Player %(player_id)d at (%(x)d, %(y)d), move=%(move)s' % (self.__dict__)

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
    TILE_EMPTY = '.'
    TILE_STONE = '#'
    TILE_SAND  = '+'
    ALL_TILES = (TILE_EMPTY, TILE_STONE, TILE_SAND)

    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.map = np.empty((self.height, self.width), dtype=object)
        self.starting_positions = dict()

    def read_map(self, inpipe):
        player_tags = [chr(x) for x in range(ord('A'), ord('Z'))]
        for c in player_tags:
            logger.debug('%s' % (repr(c),))
        for line_n in range(0, self.height):
            line = inpipe.readline()
            for col_n in range(0, len(line.strip())):
                tile = line[col_n]
                logger.debug('%s' % (repr(tile),))
                if tile in player_tags:
                    player_id = ord(tile) - ord('A')
                    self.starting_positions[player_id] = (col_n, line_n)
                    self.map[line_n, col_n] = self.TILE_EMPTY
                elif tile in self.ALL_TILES:
                    self.map[line_n, col_n] = tile
                else:
                    logger.warn('Map error: no such tile "%s"' % (repr(tile),))
                    self.map[line_n, col_n] = self.TILE_EMPTY
        logger.debug('Read map: \n%s' % (str(self.map), ))
        logger.debug('Players: %s' % (repr(self.starting_positions), ))

    def get_player_starting_position(self, player_id):
        return self.starting_positions[player_id]

    def __str__(self):
        return 'Current map=\n%s' % (str(self.map),)

class Server(object):
    INITIAL_VARS = ('number_of_players', 'max_number_of_turns', 'width', 'height')
    def __init__(self):
        self.players = list()
        self.bombs = list()
        self.width = 0
        self.height = 0
        self.map = None

    def create_players(self):
        for player_id in range(self.number_of_players):
            pos = self.map.get_player_starting_position(player_id)
            self.players.append(Player(player_id=player_id, x=pos[0], y=pos[1]))
            logger.debug('Created %s' % (repr(self.players[-1]),))

    def read_settings(self, inpipe):
        # read dimensions
        for var in self.INITIAL_VARS:
            line = inpipe.readline().split()
            setattr(self, var, int(line[0]))
        self.map = Map(self.height, self.width)
        self.map.read_map(inpipe)
        self.create_players()

    def send_initial_info(self, player, outpipe):
        """
        Send initial game status to a client
        """
        outpipe.write('%d\r\n' % (player.player_id, ))
        for var in INITIAL_VARS:
            outpipe.write('%d\r\n' % (getattr(self, var), ))

    def send_bombs(self, outpipe):
        outpipe.write('%d\r\n' % (len(self.bombs),))
        for bomb in self.bombs:
            outpipe.write('%(player_id)d %(bomb_x)d %(bomb_y)d %(bomb_ticks)d\r\n' % {'player_id': bomb.player_id, 'bomb_x': bomb.x, 'bomb_y': bomb.y, 'bomb_ticks': bomb.ticks})

    def send_players(self, outpipe):
        players_alive = 0
        for player in self.players:
            if player.alive():
                players_alive += 1
        outpipe.write('%d\r\n' % (players_alive,))

        for player in self.players:
            if player.alive():
                outpipe.write('%(player_id)d %(player_x)d %(player_y)d\r\n' % {'player_id': player.player_id, 'player_x': player.x, 'player_y': player.y})

        for player in self.players:
            if player.alive():
                outpipe.write('%(player_id)d %(move)s\r\n' % {'player_id': player.player_id, 'move': player.last_move})
            else:
                outpipe.write('%(player_id)d out\r\n' % {'player_id': player.player_id})


    def send_status_update(self, outpipe):
        """
        Send an update of the game state to a client
        """
        outpipe.write(self.map.dump())
        send_players(outpipe)
        send_bombs(outpipe)

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
        logger.debug(str(self.server.map))

if __name__ == '__main__':
    set_up_logging()
    app = ServerApp()
    app.run()
