if __name__ == "__main__":
    import os
    import sys
    sys.path.append(os.getcwd())

    import logging

    from gat_games.games.truco import *

    truco = Truco(1, [RandomTrucoPlayer('Player1'), RandomTrucoPlayer('Player2')])

    FORMAT = '%(message)s'
    logging.basicConfig(format=FORMAT)
    truco.logger.setLevel(logging.INFO)
    # truco.logger.setLevel(logging.DEBUG)

    report = truco.play()
    truco.logger.debug(report)

