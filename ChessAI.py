import random
import chess

piece_score = {"wK": 0, "wQ": 9, "wR": 5, "wB": 3, "wN": 3, "wP": 1,
               "bk": 0, "bq": 9, "br": 5, "bb": 3, "bn": 3, "bp": 1}

knight_scores = [[0.0, 0.1 , 0.2 , 0.2 , 0.2 , 0.2 , 0.1 , 0.0],
                 [0.1, 0.3 , 0.5 , 0.5 , 0.5 , 0.5 , 0.3 , 0.1],
                 [0.2, 0.5 , 0.6 , 0.65, 0.65, 0.6 , 0.5 , 0.2],
                 [0.2, 0.55, 0.65, 0.7 , 0.7 , 0.65, 0.55, 0.2],
                 [0.2, 0.5 , 0.65, 0.7 , 0.7 , 0.65, 0.5 , 0.2],
                 [0.2, 0.55, 0.6 , 0.65, 0.65, 0.6 , 0.55, 0.2],
                 [0.1, 0.3 , 0.5 , 0.55, 0.55, 0.5 , 0.3 , 0.1],
                 [0.0, 0.1 , 0.2 , 0.2 , 0.2 , 0.2 , 0.1 , 0.0]]

bishop_scores = [[0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
                 [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                 [0.2, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.2],
                 [0.2, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.2],
                 [0.2, 0.4, 0.6, 0.6, 0.6, 0.6, 0.4, 0.2],
                 [0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2],
                 [0.2, 0.5, 0.4, 0.4, 0.4, 0.4, 0.5, 0.2],
                 [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0]]

rook_scores = [[0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
               [0.5 , 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.5 ],
               [0.0 , 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0 ],
               [0.0 , 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0 ], 
               [0.0 , 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0 ],
               [0.0 , 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0 ],
               [0.0 , 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0 ],
               [0.25, 0.25, 0.25, 0.5 , 0.5 , 0.25, 0.25, 0.25]]

queen_scores = [[0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0],
                [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.4, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0]]

pawn_scores = [[0.8 , 0.8 , 0.8, 0.8 , 0.8 , 0.8, 0.8 , 0.8 ],
               [0.7 , 0.7 , 0.7, 0.7 , 0.7 , 0.7, 0.7 , 0.7 ],
               [0.3 , 0.3 , 0.4, 0.5 , 0.5 , 0.4, 0.3 , 0.3 ],
               [0.25, 0.25, 0.3, 0.45, 0.45, 0.3, 0.25, 0.25],
               [0.2 , 0.2 , 0.2, 0.4 , 0.4 , 0.2, 0.2 , 0.2 ],
               [0.25, 0.15, 0.1, 0.2 , 0.2 , 0.1, 0.15, 0.25],
               [0.25, 0.3 , 0.3, 0.0 , 0.0 , 0.3, 0.3 , 0.25],
               [0.2 , 0.2 , 0.2, 0.2 , 0.2 , 0.2, 0.2 , 0.2 ]]

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
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return -1000
        else:
            return 1000 
    if (board.is_stalemate() or board.is_insufficient_material() 
          or board.can_claim_threefold_repetition() 
          or board.is_seventyfive_moves()):
        return 0
    
    INDEX_MATRIX = [56, 57, 58, 59, 60, 61, 62, 63,
                    48, 49, 50, 51, 52, 53, 54, 55,
                    40, 41, 42, 43, 44, 45, 46, 47,
                    32, 33, 34, 35, 36, 37, 38, 39,
                    24, 25, 26, 27, 28, 29, 30, 31,
                    16, 17, 18, 19, 20, 21, 22, 23,
                     8,  9, 10, 11, 12, 13, 14, 15,
                     0,  1,  2,  3,  4,  5,  6,  7]
    
    score = 0
    for row in range(0, 8):
        for col in range(0, 8):
            piece = board.piece_at(INDEX_MATRIX[row * 8 + col])
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
    # minimax(board, valid_moves, depth,
    #                          True if board.turn == chess.WHITE else False, depth)
    
    minimax_alpha_beta(board, valid_moves, depth, -100000, 100000,
                             True if board.turn == chess.WHITE else False, depth)
    print(next_move)
    return_queue.put(next_move)

# Minimax
def minimax(board, valid_move, depth, is_maximzing_player, MAX_DEPTH):
    global next_move
    if depth == 0:
        return score_board(board)
    
    if is_maximzing_player:
        max_score = -10000 # -infinity
        
        for move in valid_move:
            board.push(move)
            next_moves = list(board.legal_moves)
            
            node_score = minimax(board, next_moves, depth - 1, not is_maximzing_player, MAX_DEPTH)
            
            if node_score > max_score:
                max_score = node_score
                if depth == MAX_DEPTH:
                    next_move = move
                
            board.pop()
        return max_score
        
    else:
        min_score = 10000 # +infinity
        
        for move in valid_move:
            board.push(move)
            next_moves = list(board.legal_moves)
            
            node_score = minimax(board, next_moves, depth - 1, not is_maximzing_player, MAX_DEPTH)
            
            if min_score > node_score:
                min_score = node_score
                if depth == MAX_DEPTH:
                    next_move = move
            
            board.pop()
        return min_score

# Alpha Beta
def minimax_alpha_beta(board, valid_move, depth, alpha, beta, is_maximzing_player, DEPTH):
    global next_move
    if depth == 0:
        return score_board(board)
    
    if is_maximzing_player:
        max_score = -10000 # -infinity
        
        for move in valid_move:
            board.push(move)
            next_moves = list(board.legal_moves)
            
            node_score = minimax_alpha_beta(board, next_moves, depth - 1, alpha, beta, not is_maximzing_player, DEPTH)
            
            if node_score > max_score:
                max_score = node_score
                if depth == DEPTH:
                    next_move = move
            
            board.pop()
            
            alpha = max(alpha, node_score)
            if beta <= alpha:
                break

        return max_score
        
    else:
        min_score = 10000 # +infinity
        
        for move in valid_move:
            board.push(move)
            next_moves = list(board.legal_moves)
            
            node_score = minimax_alpha_beta(board, next_moves, depth - 1, alpha, beta, not is_maximzing_player, DEPTH)
            
            if min_score > node_score:
                min_score = node_score
                if depth == DEPTH:
                    next_move = move
            
            board.pop()
            
            beta = min(beta, node_score)
            if beta <= alpha:
                break
            
        return min_score


def find_random_move(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]

def is_white_piece(c):
    if c in ['P', 'K', 'Q', 'R', 'N', 'B']:
        return True
    return False