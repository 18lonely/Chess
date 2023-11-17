import random

def findRandomMove(validMoves):
    return validMoves[random.randrange(0, len(validMoves))]