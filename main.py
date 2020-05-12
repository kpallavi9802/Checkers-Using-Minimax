import pygame
import numpy as np
import os
from aiclass import AI as AI
pygame.init()
import time

# GAME CONSTANTS
screen_size = (960, 600)
board_size = (600, 600)

#game color constants

WOODEN =  (160, 64, 0)
GREY = (253, 235, 208)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
ORANGE = (255, 156, 0)
BLUE = (1, 212, 180)

# CLASSES


class CheckerBoard():
    def __init__(self, surface, size, col1, col2):
        self.surface = surface
        self.board_size = size
        self.tile_size = (int(size[0]/8), int(size[1]/8))
        self.col1 = col1
        self.col2 = col2
        self.board = [[0 for x in range(8)] for y in range(8)]

    def draw(self, turn):
        for i in range(0, self.board_size[0], 2*self.tile_size[0]):
            for j in range(0, self.board_size[1], 2*self.tile_size[1]):
                pygame.draw.rect(self.surface, self.col1,
                                 (i, j, self.tile_size[0], self.tile_size[1]))
        for i in range(self.tile_size[0], self.board_size[0], 2*self.tile_size[0]):
            for j in range(self.tile_size[1], self.board_size[1], 2*self.tile_size[1]):
                pygame.draw.rect(self.surface, self.col1,
                                 (i, j, self.tile_size[0], self.tile_size[1]))

        for i in range(0, self.board_size[0], 2*self.tile_size[0]):
            for j in range(0, self.board_size[1], 2*self.tile_size[1]):
                pygame.draw.rect(self.surface, self.col2,
                                 (i+self.tile_size[0], j, self.tile_size[0], self.tile_size[1]))
        for i in range(self.tile_size[0], self.board_size[0], 2*self.tile_size[0]):
            for j in range(self.tile_size[1], self.board_size[1], 2*self.tile_size[1]):
                pygame.draw.rect(self.surface, self.col2,
                                 (i-self.tile_size[0], j, self.tile_size[0], self.tile_size[1]))

        pygame.draw.rect(self.surface, WOODEN, ((0, 0), self.board_size), 3)

    def update_board(self, ply1, ply2):
        for i in range(8):
            for j in range(8):
                if ply1[i][j] > 0:
                    self.board[i][j] = {"ply1": ply1[i][j]}
                elif ply2[i][j] > 0:
                    self.board[i][j] = {"ply2": ply2[i][j]}
                else:
                    self.board[i][j] = 0


class Player():
    def __init__(self, surface, size, num, col):
        self.surface = surface
        self.board_size = size
        self.tile_size = (int(size[0]/8), int(size[1]/8))
        self.n_men = 12
        self.n_kings = 0
        self.n_eaten = 0
        self.col = col
        self.ply = num
        self.init_pos(self.ply)

    def init_pos(self, n):
        self.pos_pieces = np.zeros(shape=(8, 8))
        if n == 1:
            for i in range(3):
                for j in range(0, 8, 2):
                    if (i == 0 or i == 2):
                        self.pos_pieces[i][j] = 1
                    elif i == 1:
                        self.pos_pieces[i][j+1] = 1
        if n == 2:
            for i in range(3):
                for j in range(0, 8, 2):
                    if (i == 0 or i == 2):
                        self.pos_pieces[7-i][j+1] = 1
                    elif i == 1:
                        self.pos_pieces[7-i][j] = 1
        self.pos_pieces = self.pos_pieces.transpose()

    def move(self, selected, moveto, board):
        moves = self.check_forced_move(board)
        if ((selected, moveto) in moves) or (len(moves) == 0):
            dead = self.check_eating_move(selected, moveto, board)
            if not dead:
                # moves without eating pieces
                if self.check_valid_move(selected, moveto, board):
                    #print("Player" + str(self.ply), "moved piece from", selected, "to", moveto)
                    # update position from selected to moveto
                    self.pos_pieces[moveto[0]][moveto[1]
                                               ] = self.pos_pieces[selected[0]][selected[1]]
                    self.pos_pieces[selected[0]][selected[1]] = 0
                    # kings promotion
                    if self.ply == 1 and moveto[1] == 7:
                        self.promote_king(moveto)
                    elif self.ply == 2 and moveto[1] == 0:
                        self.promote_king(moveto)
                    return True
                else:
                    return False
            else:
                # valid eating move
                self.n_eaten = self.n_eaten + 1
                # update position from selected to moveto
                self.pos_pieces[moveto[0]][moveto[1]] = self.pos_pieces[selected[0]][selected[1]]
                self.pos_pieces[selected[0]][selected[1]] = 0
                # kings promotion
                if self.ply == 1 and moveto[1] == 7:
                    self.promote_king(moveto)
                elif self.ply == 2 and moveto[1] == 0:
                    self.promote_king(moveto)
                return dead
        else:
            return False

    def check_forced_move(self, board):
        moves = list()
        for i in range(8):
            for j in range(8):
                if self.pos_pieces[i][j] != 0:
                    selected = (i, j)
                    for k in range(-2, 3, 4):
                        for h in range(-2, 3, 4):
                            moveto = (k+i, h+j)
                            dead = None
                            if moveto[0] >= 0 and moveto[0] < 8 and moveto[1] >= 0 and moveto[1] < 8:
                                dead = self.check_eating_move(selected, moveto, board)
                            if dead:
                                moves.append((selected, moveto))
        return moves

    def check_eating_move(self, selected, moveto, board):
        dir = (np.sign(moveto[0]-selected[0]), np.sign(moveto[1]-selected[1]))
        if self.ply == 1 and self.pos_pieces[selected[0]][selected[1]] == 1:
            if dir[1] < 0:
                return False
        elif self.ply == 2 and self.pos_pieces[selected[0]][selected[1]] == 1:
            if dir[1] > 0:
                return False
        if board[selected[0]+dir[0]][selected[1]+dir[1]] != 0 and board[selected[0]+dir[0]][selected[1]+dir[1]] != {"ply"+str(self.ply): 1} and board[selected[0]+dir[0]][selected[1]+dir[1]] != {"ply"+str(self.ply): 2}:
            if abs(selected[0]-moveto[0]) == 2 and abs(selected[1]-moveto[1]) == 2 and board[moveto[0]][moveto[1]] == 0:
                return (selected[0]+dir[0], selected[1]+dir[1])
            else:
                return False
        else:
            return False

    def check_valid_move(self, selected, moveto, board):
        if board[moveto[0]][moveto[1]] == 0:
            if board[selected[0]][selected[1]] != 0:
                if list(board[selected[0]][selected[1]].values())[0] == 2:
                    if abs(moveto[0]-selected[0]) == 1 and abs(moveto[1]-selected[1]) == 1:
                        return True
                elif list(board[selected[0]][selected[1]].values())[0] == 1:
                    if abs(moveto[0]-selected[0]) == 1:
                        if self.ply == 1 and (moveto[1]-selected[1]) == 1:
                            return True
                        elif self.ply == 2 and (moveto[1]-selected[1]) == -1:
                            return True
                return False
            else:
                return False

    def promote_king(self, pos):
        self.pos_pieces[pos[0]][pos[1]] = 2

    def update_dead(self, dead):
        if not (dead is True or dead is False):
            self.pos_pieces[dead[0]][dead[1]] = 0

    def draw(self):
        for i in range(8):
            for j in range(8):
                if self.pos_pieces[i][j] == 1:
                    centre = (i*self.tile_size[0]+int(self.tile_size[0]/2),
                              j*self.tile_size[1]+int(self.tile_size[1]/2))
                    radius = int(self.tile_size[0]/2*(7/8))
                    pygame.draw.circle(self.surface, self.col, centre, radius)
                elif self.pos_pieces[i][j] == 2:
                    centre = (i*self.tile_size[0]+int(self.tile_size[0]/2),
                              j*self.tile_size[1]+int(self.tile_size[1]/2))
                    radius = int(self.tile_size[0]/2*(7/8))
                    pygame.draw.circle(self.surface, self.col, centre, radius)
                    invcol = (255-self.col[0], 255-self.col[1], 255-self.col[2])
                    radius = int(self.tile_size[0]/2*(2/8))
                    pygame.draw.circle(self.surface, invcol, centre, radius)
                    pygame.draw.circle(self.surface, invcol, (centre[0]+8, centre[1]), radius)
                    pygame.draw.circle(self.surface, invcol, (centre[0], centre[1]+8), radius)
                    pygame.draw.circle(self.surface, invcol, (centre[0]-8, centre[1]), radius)
                    pygame.draw.circle(self.surface, invcol, (centre[0], centre[1]-8), radius)

# FUNCTIONS


def select_piece(surface, player, selected, moveto, event):
    pos = event.__dict__['pos']
    posgrid = (int(pos[0]/player.tile_size[0]), int(pos[1]/player.tile_size[1]))
    if selected is None and moveto is None:
        if player.pos_pieces[posgrid[0], posgrid[1]]:
            return posgrid
        else:
            return False
    elif selected is not None and moveto is None:
        return posgrid
    else:
        return False


def draw_selected(surface, posgrid, player):
    if player.pos_pieces[posgrid[0], posgrid[1]]:
        col = (player.col[0], player.col[1], player.col[2])
        rect = (posgrid[0]*player.tile_size[0], posgrid[1]*player.tile_size[1],
                player.tile_size[0], player.tile_size[1])
        pygame.draw.rect(surface, col, rect, 3)
        pygame.display.flip()


def switch_turn(board, turn, sel):
    if turn == player1:
        type = list(board.board[sel[0]][sel[1]].values())[0]
        near_enemy = list()
        dir_enemy = list()
        for i in range(-1, 2, 2):
            for j in range(-1, 2, 2):
                if (sel[0]+i >= 0 and sel[0]+i < 8) and (sel[1]+j >= 0 and sel[1]+j < 8):
                    if board.board[sel[0]+i][sel[1]+j] == {"ply2": 1} or board.board[sel[0]+i][sel[1]+j] == {"ply2": 2}:
                        near_enemy.append((sel[0]+i, sel[1]+j))
                        dir_enemy.append((i, j))
                        newpos = (near_enemy[-1][0]+dir_enemy[-1][0],
                                  near_enemy[-1][1]+dir_enemy[-1][1])
                        if newpos[0] >= 0 and newpos[0] < 8 and newpos[1] >= 0 and newpos[1] < 8:
                            if board.board[newpos[0]][newpos[1]] == 0:
                                if type == 1 and dir_enemy[-1][1] == -1:
                                    pass
                                else:
                                    return player1
        return player2
    elif turn == player2:
        type = list(board.board[sel[0]][sel[1]].values())[0]
        near_enemy = list()
        dir_enemy = list()
        for i in range(-1, 2, 2):
            for j in range(-1, 2, 2):
                if (sel[0]+i >= 0 and sel[0]+i < 8) and (sel[1]+j >= 0 and sel[1]+j < 8):
                    if board.board[sel[0]+i][sel[1]+j] == {"ply1": 1} or board.board[sel[0]+i][sel[1]+j] == {"ply1": 2}:
                        near_enemy.append((sel[0]+i, sel[1]+j))
                        dir_enemy.append((i, j))
                        newpos = (near_enemy[-1][0]+dir_enemy[-1][0],
                                  near_enemy[-1][1]+dir_enemy[-1][1])
                        if newpos[0] >= 0 and newpos[0] < 8 and newpos[1] >= 0 and newpos[1] < 8:
                            if board.board[newpos[0]][newpos[1]] == 0:
                                if type == 1 and dir_enemy[-1][1] == 1:
                                    pass
                                else:
                                    return player2
        return player1


def copy_board(board):
    copy = [[0 for x in range(8)] for y in range(8)]
    for i in range(8):
        for j in range(8):
            copy[i][j] = board[i][j]
    return copy


def clear_screen():
    os.system('cls')


def print_score(ply1, ply2):
    str1 = str(ply1.n_eaten)
    str2 = str(ply2.n_eaten)+" "
    if ply1.n_eaten >= 10:
        str1 = str1 + " "
    if ply2.n_eaten >= 10:
        str2 = str(ply2.n_eaten)
    update_score_board(screen,str1,18, 800, 140)
    update_score_board(screen, str1, 18, 800, 190)
    if ply1.n_eaten == 15:
        print("\n\n\tPLAYER1 WIN!")
    elif ply2.n_eaten == 15:
        print("\n\n\tPLAYER2 WIN!")



##########score

def button( cur, x, y, w, h, action):
    if x + w > cur[0] > x and y + w >cur[1] > y:
        if action!=None:
            if action=="quit":
                pygame.quit()


pygame.font.init()
#font=pygame.font.SysFont("Comic sans ms", 16)

smallfont = pygame.font.SysFont("Helvetica", 18)
medfont = pygame.font.SysFont("Helvetica", 32)
largefont = pygame.font.SysFont("comicsansms", 60)

def text_objects(text, color, size="small"):
    if size == "small":
        textSurface = smallfont.render(text, True, color)
    if size == "medium":
        textSurface = medfont.render(text, True, color)
    if size == "large":
        textSurface = largefont.render(text, True, color)

    return textSurface, textSurface.get_rect()

def text_to_button(msg, color, buttonx, buttony, buttonwidth, buttonheight, size="medium"):
    textSurf, textRect = text_objects(msg, color, size)
    textRect.center = ((buttonx + (buttonwidth // 2)), buttony + (buttonheight // 2))
    screen.blit(textSurf, textRect)

def msg_to_screen(msg, color, x, y, size="small"):
    textSurf, textRect = text_objects(msg, color, size)
    screen.blit(textSurf, (x, y))

font_name=pygame.font.match_font('arial')
def update_score_board(surf,text,size,x,y,):
    font = pygame.font.Font(font_name,size)

    text_surface=font.render(text,True,BLUE)
    for i in range(-15,15):
        screen.fill((0,0,0), rect=text_surface.get_rect(topleft=(x+i,y)))
    text_rect= text_surface.get_rect()
    text_rect.midtop=(x,y)
    surf.blit(text_surface,text_rect)

def print_score(ply1, ply2):
    str1 = str(ply1.n_eaten)
    str2 = str(ply2.n_eaten)+" "
    if ply1.n_eaten >= 10:
        str1 = str1 + " "
    if ply2.n_eaten >= 10:
        str2 = str(ply2.n_eaten)
    update_score_board(screen,str1,18, 800, 140)
    update_score_board(screen, str2, 18, 800, 190)
    if ply1.n_eaten == 11:
        update_score_board(screen,"WON",18, 800, 140)
    elif ply2.n_eaten == 11:
        update_score_board(screen, "WON", 18, 800, 190)


if __name__ == "__main__":
    pygame.display.init()
    clear_screen()
    pygame.display.set_caption('Checker Using Minimax Algorithm')
    screen = pygame.display.set_mode(screen_size)
    screen.fill(BLACK)
    clock = pygame.time.Clock()

    gameboard = CheckerBoard(screen, board_size, WOODEN, GREY)
    player1 = Player(screen, board_size, 1, WHITE)
    player2 = Player(screen, board_size, 2, BLACK)

    AIbot = AI("hard", 1)

    gameboard.update_board(player1.pos_pieces, player2.pos_pieces)

    selected = None
    moveto = None
    if np.random.randint(1, 3) == 1:
        Player_turn = player1
        update_score_board(screen,"Player1",18, 800, 90)
    else:
        Player_turn = player2
        update_score_board(screen,"Player2",18, 800, 90)

    while(True):
        print_score(player1, player2)
        gameboard.draw(Player_turn)
        player1.draw()
        player2.draw()

        msg_to_screen("Turn : ", WHITE, 680, 90)
        msg_to_screen("AI Score :", WHITE, 680, 140)
        msg_to_screen("Your Score : ", WHITE, 680, 190)
        msg_to_screen("Total nodes Explored  ", WHITE, 697, 260)
        pygame.draw.ellipse(screen, WOODEN, (710, 350, 100, 50))
        text_to_button("QUIT", BLACK, 710, 350, 100, 50)


        if selected:
            draw_selected(screen, selected, Player_turn)

        # detect mouse event
        for event in pygame.event.get():
            if event.type == pygame.QUIT :
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                cur = pygame.mouse.get_pos()
                click = pygame.mouse.get_pressed()
                if click[0] == 1:
                    if 600 > cur[0] >0 and 600> cur[1] > 0:
                        if not selected:
                            selected = select_piece(screen, Player_turn, selected, moveto, event)
                        elif selected:
                            tmp = select_piece(screen, Player_turn, selected, moveto, event)
                            if tmp != selected:
                                moveto = tmp
                    else :
                        button(cur,710, 350, 100, 50, action="quit")

        # AIbot's turn
        if Player_turn == player1:
            board = copy_board(gameboard.board)
            try:
                valMove, aiMove = AIbot.minimax(board, 100, True)
                nodes=AIbot.explored_node()
                update_score_board(screen, str(nodes), 18, 780,290)
                selected = aiMove[0]
                moveto = aiMove[1]
            except TypeError:
                Selected = None
                moveto = None

        # move piece
        if moveto is not None:
            if Player_turn == player1:
                tmp = player1.move(selected, moveto, gameboard.board)
                player2.update_dead(tmp)
            elif Player_turn == player2:
                tmp = player2.move(selected, moveto, gameboard.board)
                player1.update_dead(tmp)

            # update the position of the player's pieces
            gameboard.update_board(player1.pos_pieces, player2.pos_pieces)

            if tmp is not False:
                clear_screen()
                if type(tmp) == tuple:
                    Player_turn = switch_turn(gameboard, Player_turn, moveto)
                    if Player_turn == player1:
                        update_score_board(screen,"Player1",18, 800, 90)
                    else:
                        update_score_board(screen,"Player2",18, 800, 90)

                else:
                    if Player_turn == player1:
                        Player_turn = player2
                        update_score_board(screen,"Player2",18, 800, 90)


                    else:
                        Player_turn = player1
                        update_score_board(screen,"Player1",18, 800, 90)

            moveto = None
            selected = None
        pygame.display.flip()