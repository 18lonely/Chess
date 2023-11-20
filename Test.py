import pygame as p
import pygame_menu
import chess
import sys

MENU_PANEL_WIDTH = 380
MENU_PANEL_HEIGHT = 512
BOARD_WIDTH = 512
BOARD_HEIGHT = 512
DIMENSION = 8
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 60
IMAGES = {}
SIZE_WALL = 24

p.init()
screen = p.display.set_mode((BOARD_WIDTH + 2 * SIZE_WALL, BOARD_HEIGHT + 2 * SIZE_WALL)) 
clock = p.time.Clock()

def loadImages():
    """
    Khai báo hình ảnh
    """
    pieces = ['P', 'R', 'N', 'B', 'K', 'Q', 'p', 'r', 'n', 'b', 'k', 'q']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))

def loadWall(screen):
    wall = p.transform.scale(p.image.load("images/wall.png"), (BOARD_WIDTH + 2 * SIZE_WALL, BOARD_HEIGHT + 2 * SIZE_WALL))
    screen.blit(wall, p.Rect(0, 0, BOARD_WIDTH + 2 * SIZE_WALL, BOARD_HEIGHT + 2 * SIZE_WALL))

def startGame():
    screen.fill(p.Color("white"))
    
    board = chess.Board()
    
    valid_moves = list(board.legal_moves)
    move_made = False
    animate = False
    loadImages()
    loadWall(screen)
    
    running = True
    
    square_selected = () 
    player_clicks = [] 
    
    game_over = False
    ai_thinking = False
    move_undone = False
    move_finder_process = None
    
    player_one = True  # Nếu là Humen Trắng : True. Nếu là AI : False
    player_two = True  # Nếu là Hymen Đen: True. Nếu là AI: false
    
    while running:
        human_turn = (board.turn == chess.WHITE and player_one) or (board.turn == chess.BLACK and player_two)
        event_list = p.event.get()

        for e in event_list:
            if e.type == p.QUIT:
                p.quit()
                sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()  # (x, y): vị trí click
                    col = (location[0] - SIZE_WALL) // SQUARE_SIZE 
                    row = (location[1] - SIZE_WALL) // SQUARE_SIZE
                    if square_selected == (row, col) or col >= 8:  # Click giống nhau 2 ô liên tiếp 
                        square_selected = ()  # Xoá ô đã chọn
                        player_clicks = []  # Hoàn tác click
                    else:
                        square_selected = (row, col)
                        player_clicks.append(square_selected)  # Thêm ô đã click
                    if len(player_clicks) == 2 and human_turn:  # Sau khi click 2 lần
                        move = chess.Move.from_uci(getRankFile(player_clicks[0][0], player_clicks[0][1]) + getRankFile(player_clicks[1][0], player_clicks[1][1]))
                        is_promotion_move = chess.Move.from_uci(str(move) + 'q')
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i] or is_promotion_move == valid_moves[i]:
                                board.push(valid_moves[i])
                                move_made = True
                                animate = True
                                square_selected = ()  # Hoàn tác click
                                player_clicks = []
                        if not move_made:
                            player_clicks = [square_selected]
            # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # Undo move Ctrl + z
                    if(len(board.move_stack) > 0):
                        board.pop()
                        move_made = True
                        animate = False
                        game_over = False
                        if ai_thinking:
                            move_finder_process.terminate()
                            ai_thinking = False
                        move_undone = True
                            
                if e.key == p.K_r:  # Reset trò chơi Ctrl + r
                    board = chess.Board()
                    valid_moves = list(board.legal_move)
                    square_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True

            # AI move finder
            if not game_over and not human_turn and not move_undone:
                if not ai_thinking:
                    ai_thinking = True
                    # return_queue = Queue()  # used to pass data between threads
                    # move_finder_process = Process(target=ChessAI.findBestMove, args=(game_state, valid_moves, return_queue))
                    # move_finder_process.start()

            # if not move_finder_process.is_alive():
            #     ai_move = return_queue.get()
            #     if ai_move is None:
            #         ai_move = ChessAI.findRandomMove(valid_moves)
            #     game_state.makeMove(ai_move)
            #     move_made = True
            #     animate = True
            #     ai_thinking = False

            if move_made:
                if animate:
                    animateMove(getPosition(str(board.move_stack[-1])), screen, make_matrix(board), clock)
                valid_moves = list(board.legal_moves)
                move_made = False
                animate = False
                move_undone = False

        drawGameState(screen, make_matrix(board), valid_moves, square_selected, board.turn)

        if board.is_checkmate():
            game_over = True
            if board.turn == chess.WHITE:
                drawEndGameText(screen, "Black wins by checkmate")
            else:
                drawEndGameText(screen, "White wins by checkmate")
        elif board.is_stalemate() or board.is_insufficient_material() or board.can_claim_threefold_repetition() or board.is_fivefold_repetition() or board.is_seventyfive_moves():
            game_over = True
            drawEndGameText(screen, "Stalemate")
        
        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, board, valid_moves, square_selected, turn):
    """
    Responsible for all the graphics within current game state.
    """
    drawBoard(screen)  # Vẽ các ô của bàn cờ
    highlightSquares(screen, board, valid_moves, square_selected, turn)
    drawPieces(screen, board)  # Vẽ các quân cờ


def drawBoard(screen):
    """
    Draw the squares on the board.
    The top left square is always light.
    """
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[((row + column) % 2)]
            p.draw.rect(screen, color, p.Rect(column * SQUARE_SIZE + SIZE_WALL, row * SQUARE_SIZE + SIZE_WALL, SQUARE_SIZE, SQUARE_SIZE))

def isWhitePiece(c):
    if c in ['P', 'K', 'Q', 'R', 'N', 'B']:
        return True
    return False


def highlightSquares(screen, board, valid_moves, square_selected, turn):
    if square_selected != ():
        row, col = square_selected
        if (isWhitePiece(board[row][col][0]) and turn == chess.WHITE) or (not isWhitePiece(board[row][col][0]) and turn == chess.BLACK):  # square_selected is a piece that can be moved
            # Highlight ô được chọn
            s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(100)  # 0 - 255
            s.fill(p.Color('blue'))
            screen.blit(s, (col * SQUARE_SIZE + SIZE_WALL, row * SQUARE_SIZE + SIZE_WALL))
            # Highlight ô bắt đầu đi và ô kết thúc
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                position = getPosition(str(move))
                if position[0] == row and position[1] == col:
                    screen.blit(s, (position[3] * SQUARE_SIZE + SIZE_WALL, position[2] * SQUARE_SIZE + SIZE_WALL))


def drawPieces(screen, board):
    """
    Draw the pieces on the board using the current game_state.board
    """
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != ".":
                screen.blit(IMAGES[piece], p.Rect(column * SQUARE_SIZE + SIZE_WALL, row * SQUARE_SIZE + SIZE_WALL, SQUARE_SIZE, SQUARE_SIZE))

def drawText(screen, text, position, color, fontSize):
    font = p.font.SysFont("arial", fontSize)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = position
    screen.blit(text_surface, text_rect)


def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, False, p.Color("gray"))
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - text_object.get_width() / 2,
                                                                 BOARD_HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, False, p.Color('black'))
    screen.blit(text_object, text_location.move(2, 2))


def animateMove(move, screen, board, clock):
    """
    Animating a move
    """
    global colors
    d_row = move[2] - move[0]
    d_col = move[3] - move[1]
    frames_per_square = 5  # Frames to move one square
    frame_count = (abs(d_row) + abs(d_col)) * frames_per_square
    for frame in range(frame_count + 1):
        row, col = (move[0] + d_row * frame / frame_count, move[1] + d_col * frame / frame_count)
        drawBoard(screen)
        drawPieces(screen, board)
        # Xoá quân cờ ở ô bắt đầu
        color = colors[(move[2] + move[3]) % 2]
        end_square = p.Rect(move[3] * SQUARE_SIZE + SIZE_WALL, move[2] * SQUARE_SIZE + SIZE_WALL, SQUARE_SIZE, SQUARE_SIZE)
        p.draw.rect(screen, color, end_square)

        # Thực hiện vẽ các Animation
        screen.blit(IMAGES[board[move[2]][move[3]]], p.Rect(col * SQUARE_SIZE + SIZE_WALL, row * SQUARE_SIZE + SIZE_WALL, SQUARE_SIZE, SQUARE_SIZE))
        p.display.flip()
        clock.tick(60)

def getRankFile(row, col):
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}
    
    return cols_to_files[col] + rows_to_ranks[row]

def getPosition(file):
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    
    return (ranks_to_rows[file[1]], files_to_cols[file[0]], ranks_to_rows[file[3]], files_to_cols[file[2]])

def make_matrix(board): 
    #type(board) == chess.Board()
    pgn = board.epd()
    result = [] 
    pieces = pgn.split(" ", 1)[0]
    rows = pieces.split("/")
    for row in rows:
        subResult = [] 
        for thing in row:
            if thing.isdigit():
                for i in range(0, int(thing)):
                    subResult.append('.')
            else:
                subResult.append(thing)
        result.append(subResult)
    return result

def options():
    pass

menu = pygame_menu.Menu('Chess', BOARD_WIDTH + 2 * SIZE_WALL, BOARD_HEIGHT + 2 * SIZE_WALL,
                       theme=pygame_menu.themes.THEME_BLUE)


menu.add.button('Play', startGame)
menu.add.button('Options', options)
menu.add.button('Quit', pygame_menu.events.EXIT)

menu.mainloop(screen)