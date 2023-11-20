import random
import chess

CHECKMATE = 1000
STALEMATE = 0

piece_score = {"wK": 0, "wQ": 9, "wR": 5, "wB": 3, "wN": 3, "wP": 1,
               "bk": 0, "bq": 9, "br": 5, "bb": 3, "bn": 3, "bp": 1}

knight_scores = [[0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0],
                 [0.1, 0.3, 0.5, 0.5, 0.5, 0.5, 0.3, 0.1],
                 [0.2, 0.5, 0.6, 0.65, 0.65, 0.6, 0.5, 0.2],
                 [0.2, 0.55, 0.65, 0.7, 0.7, 0.65, 0.55, 0.2],
                 [0.2, 0.5, 0.65, 0.7, 0.7, 0.65, 0.5, 0.2],
                 [0.2, 0.55, 0.6, 0.65, 0.65, 0.6, 0.55, 0.2],
                 [0.1, 0.3, 0.5, 0.55, 0.55, 0.5, 0.3, 0.1],
                 [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0]]

bishop_scores = [[0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
                 [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                 [0.2, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.2],
                 [0.2, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.2],
                 [0.2, 0.4, 0.6, 0.6, 0.6, 0.6, 0.4, 0.2],
                 [0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2],
                 [0.2, 0.5, 0.4, 0.4, 0.4, 0.4, 0.5, 0.2],
                 [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0]]

rook_scores = [[0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
               [0.5, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.5],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.25, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.25]]

queen_scores = [[0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0],
                [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.4, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0]]

pawn_scores = [[0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
               [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
               [0.3, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.3],
               [0.25, 0.25, 0.3, 0.45, 0.45, 0.3, 0.25, 0.25],
               [0.2, 0.2, 0.2, 0.4, 0.4, 0.2, 0.2, 0.2],
               [0.25, 0.15, 0.1, 0.2, 0.2, 0.1, 0.15, 0.25],
               [0.25, 0.3, 0.3, 0.0, 0.0, 0.3, 0.3, 0.25],
               [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]]

piece_position_scores = {"wN": knight_scores,
                         "bn": knight_scores[::-1],
                         "wB": bishop_scores,
                         "bb": bishop_scores[::-1],
                         "wQ": queen_scores,
                         "bq": queen_scores[::-1],
                         "wR": rook_scores,
                         "br": rook_scores[::-1],
                         "wP": pawn_scores,
                         "bp": pawn_scores[::-1]}

def score_board(board):
    """
    Score the board. A positive score is good for white, a negative score is good for black.
    """
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return -CHECKMATE  # Đen thắng
        else:
            return CHECKMATE  # Trắng thắng
    elif board.is_stalemate():
        return STALEMATE
    score = 0
    
    i = 0
    for row in range(0, 8):
        for col in range(0, 8):
            piece = board.piece_at(row * 8 + col)
            if piece != None:
                piece = str(piece)
                color = 'w' if is_white_piece(piece) else 'b'
                piece_position_score = 0
                if piece != "K" and piece != 'k':
                    piece_position_score = piece_position_scores[color + piece][row][col]
                if color == 'w':
                    score += piece_score[color + piece] + piece_position_score
                if color != 'w':
                    score -= piece_score[color + piece] + piece_position_score

    return score

def findBestMove(board, valid_moves, return_queue, depth):
    global next_move
    next_move = None
    random.shuffle(valid_moves)
    minimax(board, valid_moves, depth,
                             True if board.turn == chess.WHITE else False, depth)
    return_queue.put(next_move)

# Minimax
def minimax(board, valid_move, depth, is_maximzing_player, DEPTH):
    global next_move
    if depth == 0:
        return score_board(board)
    
    if is_maximzing_player:
        max_score = -10000 # -infinity
        
        for move in valid_move:
            board.push(move)
            next_moves = list(board.legal_moves)
            
            node_score = minimax(board, next_moves, depth - 1, not is_maximzing_player, DEPTH)
            
            if node_score > max_score:
                max_score = node_score
                if depth == DEPTH:
                    next_move = move
                
            board.pop()
        return max_score
        
    else:
        min_score = 10000 # +infinity
        
        for move in valid_move:
            board.push(move)
            next_moves = list(board.legal_moves)
            
            node_score = minimax(board, next_moves, depth - 1, not is_maximzing_player, DEPTH)
            
            if min_score > node_score:
                min_score = node_score
                if depth == DEPTH:
                    next_move = move
            
            board.pop()
        return min_score
    

def find_random_move(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]

def is_white_piece(c):
    if c in ['P', 'K', 'Q', 'R', 'N', 'B']:
        return True
    return False