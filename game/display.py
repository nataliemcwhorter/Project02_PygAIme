import pygame
import numpy as np

"""
This is the Connect4Display class
it creates the GUI and the visible elements of this ai
it uses pygame to create it.
"""
class Connect4Display:
    def __init__(self, screen, rows=6, cols=7):
        self.screen = screen
        self.rows = rows
        self.cols = cols
        self.BLUE = (0, 0, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 255, 0)
        self.WHITE = (255, 255, 255)
        self.SQUARESIZE = 80
        self.width = cols * self.SQUARESIZE
        self.height = (rows + 1) * self.SQUARESIZE

    """
    draw_board(self, board) creates the game board that will be displayed on the screen
    board is the board (where the pieces are and who they belong to)
    """
    def draw_board(self, board):
        pygame.draw.rect(self.screen, self.BLUE, pygame.Rect(0, self.SQUARESIZE, self.width, self.height-self.SQUARESIZE))
        for row in range(self.rows):
            for col in range(self.cols):
                #calculate pixel position
                #draw dircle based on board[row[col]
                center_x = (col * self.SQUARESIZE) + self.SQUARESIZE//2
                center_y = ((row + 1) * self.SQUARESIZE) + self.SQUARESIZE//2
                if board[row][col] == 0:
                    color = self.BLACK
                elif board[row][col] == 1:
                    color = self.RED
                elif board[row][col] == 2:
                    color = self.YELLOW
                pygame.draw.circle(self.screen, color, (center_x, center_y), self.SQUARESIZE // 2 - 5)

    """
    draw_piece_preview(self, col, player) draws the piece hovering over the column your mouse is on
    col is the column number
    player is the player so that we know what color to make the piece
    """
    def draw_piece_preview(self, col, player):
        center_x = (col * self.SQUARESIZE) + self.SQUARESIZE//2
        center_y = self.SQUARESIZE//2
        if player == 1:
            color = self.RED
        elif player == 2:
            color = self.YELLOW
        pygame.draw.circle(self.screen, color, (center_x, center_y), self.SQUARESIZE // 2 - 5)

    """
    get_column_from_mouse(self, mouse_x) finds which column the user is hovering over
    mouse_x is the x position of the mouse
    """
    def get_column_from_mouse(self, mouse_x):
        column = mouse_x // self.SQUARESIZE
        if column < 0 or column >= self.cols:
            column = -1
        return column

    """
    draw_game_over_screen(self, winner) draws the screen for when the game is over
    winner is whoever won the game
    displays a different screen based on if the player or the computer won
    """
    def draw_game_over_screen(self, winner):
        overlay = pygame.Surface((800, 600))
        overlay.set_alpha(128)
        overlay.fill(self.BLACK)
        self.screen.blit(overlay, (0, 0))
        font = pygame.font.Font(None, 72)
        if winner == 1:
            message = "RED PLAYER WINS!"
            color = self.RED
        elif winner == 2:
            message = "YELLOW PLAYER WINS!"
            color = self.YELLOW
        else:
            message = "ITS A TIE!"
            color = self.WHITE
        text = font.render(message, True, color)
        text_rect = text.get_rect(center=(400,300))
        self.screen.blit(text, text_rect)
        small_font = pygame.font.Font(None, 36)
        restart_text = small_font.render("press SPACE to play again", True, self.WHITE)
        restart_rect = restart_text.get_rect(center=(400,400))
        self.screen.blit(restart_text, restart_rect)

    """
    draw_menu(self, menu_items, selected_index) draws the main menu for the user then to choose
    from the options displayed
    menu_items is a list of the different options that will be choices in the menu
    selected_index is the index of the selected option (appears as a different color)
    """
    def draw_menu(self, menu_items, selected_index=0):
        self.screen.fill(self.BLACK)
        font = pygame.font.Font(None, 36)
        for i, item in enumerate(menu_items):
            if i == selected_index:
                color = self.RED
            else:
                color = self.WHITE
            text = font.render(item, True, color)
            y_pos = 200 + i * 50
            self.screen.blit(text, (100, y_pos))

    """
    draw_training_info(self, episode, epsilon, win_rate) draws the training info
    episode is the current episode
    epsilon is the current epsilon
    win_rate is the current win rate
    """
    def draw_training_info(self, episode, epsilon, win_rate):
        font = pygame.font.Font(None, 24)
        episode_text = font.render(f"Episode: {episode}", True, self.WHITE)
        epsilon_text = font.render(f"Exploration: {epsilon:.3f}", True, self.WHITE)
        winrate_text = font.render(f"Winrate: {win_rate:.1f}", True, self.WHITE)
        self.screen.blit(episode_text, (600, 20))
        self.screen.blit(epsilon_text, (600, 50))
        self.screen.blit(winrate_text, (600, 80))

    """
    draw_save_prompt() draws the prompt to save the model
    """
    def draw_save_prompt(self):
        overlay = pygame.Surface((400, 200))
        overlay.set_alpha(200)
        overlay.fill(self.BLACK)
        overlay_rect = overlay.get_rect(center=(400, 300))
        self.screen.blit(overlay, overlay_rect)
        font = pygame.font.Font(None, 48)
        prompt_text = font.render("save model?", True, self.WHITE)
        prompt_rect = prompt_text.get_rect(center=(400, 280))
        self.screen.blit(prompt_text, prompt_rect)
        small_font = pygame.font.Font(None, 32)
        instruction_text = small_font.render("Press Y to save, N to skip", True, self.WHITE)
        instruction_rect = instruction_text.get_rect(center=(400, 320))
        self.screen.blit(instruction_text, instruction_rect)