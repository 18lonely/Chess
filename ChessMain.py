import pygame as p
import pygame_menu
import chess
import sys
import ChessAI
from multiprocessing import Process, Queue

BOARD_WIDTH = 512
BOARD_HEIGHT = 512
DIMENSION = 8
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 60
IMAGES = {}
SIZE_WALL = 24

p.init()

global screen

# Globle Vars
global menu

global player_one  # False nếu trắng là AI
global depth_for_white
global player_two  # False nếu trắng là AI
global depth_for_black


player_one = True
depth_for_white = 3
player_two = True
depth_for_black = 3

def loadImages():
    """
    Khai báo hình ảnh
    """
    pieces = ['wP', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'br', 'bn', 'bb', 'bk', 'bq']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))

def loadWall(screen):
    wall = p.transform.scale(p.image.load("images/wall.png"), (BOARD_WIDTH + 2 * SIZE_WALL, BOARD_HEIGHT + 2 * SIZE_WALL))
    screen.blit(wall, p.Rect(0, 0, BOARD_WIDTH + 2 * SIZE_WALL, BOARD_HEIGHT + 2 * SIZE_WALL))

def startGame():
    global menu
    global screen

    clock = p.time.Clock()

    screen.fill(p.Color("white"))
    board = chess.Board()
    valid_moves = list(board.legal_moves)
    move_made = False
    animate = False
    loadImages()
    loadWall(screen)

    square_selected = ()
    player_clicks = []

    game_over = False
    ai_thinking = False
    move_undone = False
    move_finder_process = None

    global player_one
    global player_two
    global depth_for_white
    global depth_for_black
    
    running = True
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
                                print(ChessAI.score_board(board))
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
                    menu.enable()
                    return

        # AI move finder
        if not game_over and not human_turn and not move_undone:
            depth_turn = depth_for_white if board.turn == chess.WHITE else depth_for_black
            if not ai_thinking:
                ai_thinking = True
                return_queue = Queue()
                move_finder_process = Process(target=ChessAI.findBestMove, args=(board, list(board.legal_moves), return_queue, depth_turn))
                move_finder_process.start()

            if not move_finder_process.is_alive():
                ai_move = return_queue.get()
                if ai_move is None:
                    ai_move = ChessAI.find_random_move(valid_moves)
                board.push(ai_move)
                print(ChessAI.score_board(board))
                move_made = True
                animate = True
                ai_thinking = False

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
        elif board.is_stalemate() or board.is_insufficient_material() or board.can_claim_threefold_repetition() or board.is_seventyfive_moves():
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
            s.fill(p.Color('pink'))
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
            piece = 'w' + board[row][column] if isWhitePiece(board[row][column]) else 'b' + board[row][column]
            if piece[1] != ".":
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
        piece = 'w' + board[move[2]][move[3]] if isWhitePiece(board[move[2]][move[3]]) else 'b' + board[move[2]][move[3]]
        screen.blit(IMAGES[piece], p.Rect(col * SQUARE_SIZE + SIZE_WALL, row * SQUARE_SIZE + SIZE_WALL, SQUARE_SIZE, SQUARE_SIZE))
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

def setPlayerWhite(selected, value):
    global player_one
    player_one = value

def setDepthForWhite(value):
    global depth_for_white
    depth_for_white = int(value)

def setPlayerBlack(selected, value):
    global player_two
    player_two = value

def setDepthForBlack(value):
    global depth_for_black
    depth_for_black = int(value)

def main():
    global screen
    global menu
    screen = p.display.set_mode((BOARD_WIDTH + 2 * SIZE_WALL, BOARD_HEIGHT + 2 * SIZE_WALL))

    menu = pygame_menu.Menu('Chess', BOARD_WIDTH + 2 * SIZE_WALL, BOARD_HEIGHT + 2 * SIZE_WALL,
                            theme=pygame_menu.themes.THEME_BLUE)

    menu.add.button('Play', startGame)
    menu.add.selector('White: ', [('Humen', True), ('AI', False)], onchange=setPlayerWhite)
    menu.add.range_slider('Depth: ', default=3, range_values=(1, 10), increment=1, value_format=lambda x: str(int(x)),
                          onchange=setDepthForWhite)
    menu.add.selector('Black: ', [('Humen', True), ('AI', False)], onchange=setPlayerBlack)
    menu.add.range_slider('Depth: ', default=3, range_values=(1, 10), increment=1, value_format=lambda x: str(int(x)),
                          onchange=setDepthForBlack)
    menu.add.button('Quit', pygame_menu.events.EXIT)

    while True:
        events = p.event.get()
        for event in events:
            if event.type == p.QUIT:
                exit()

        if menu.is_enabled():
            menu.update(events)
            menu.draw(screen)

        p.display.update()

if __name__ == '__main__':
    main()