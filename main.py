import random
import pygame
import sys
from ai.training import TrainingManager
from game.board import Connect4Board
from ai.q_agent import QAgent
from game.display import Connect4Display
from utils.file_manager import ModelManager


class GameManager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Connect 4 AI")
        self.clock = pygame.time.Clock()
        self.board = Connect4Board()
        self.display = Connect4Display(self.screen)
        self.agent = QAgent()
        self.model_manager = ModelManager()
        self.trainer = TrainingManager(self.agent, self.board)
        self.state = "MENU"
        self.menu_selection = 0
        self.menu_options = ["train new model", "load existing model", "play vs ai", "manage models", "quit"]
        self.current_player = 2
        self.game_over = False
        self.load_existing = False

    def show_main_menu(self):
        self.screen.fill((0, 0, 0))
        self.display.draw_menu(self.menu_options, self.menu_selection)

    def training_mode(self):
        if self.load_existing:
            # TODO: Show model selection and load chosen model
            saved_models = self.model_manager.list_saved_models()
            if saved_models:
                selected_model = saved_models[0]
                self.agent.load_model(selected_model['path'])
            else:
                self.load_existing = False
        if not self.load_existing:
            self.agent = QAgent()
        total_episodes = 5000
        save_interval = 500
        for episode in range(total_episodes):
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = "MENU"
                        return
                    elif event.key == pygame.K_s:
                        self.display.draw_save_prompt()
                        pygame.display.flip()
                        waiting_for_save = True
                        while waiting_for_save:
                            for save_event in pygame.event.get():
                                if save_event.type == pygame.KEYDOWN:
                                    if save_event.key == pygame.K_y:
                                        model_name = self.model_manager.generate_model_name()
                                        self.model_manager.save_model(
                                            self.agent,
                                            model_name,
                                            {
                                                'episode': episode,
                                                'win_rate': self.trainer.get_training_progress()['win_rate']
                                            }
                                        )
                                        waiting_for_save = False
                                    elif save_event.key == pygame.K_n:
                                        waiting_for_save = False
            self.trainer.self_play_episode()
            if episode % save_interval == 0:
                model_name = self.model_manager.generate_model_name()
                self.model_manager.save_model(
                    self.agent,
                    model_name,
                    {
                        'episode': episode,
                        'win_rate': self.trainer.get_training_progress()['win_rate']
                    }
                )
            self.screen.fill((0, 0, 0))
            progress = self.trainer.get_training_progress()
            self.display.draw_training_info(
                episode,
                self.agent.epsilon,
                progress['win_rate']
            )
            pygame.display.flip()
            self.clock.tick(60)
        self.state = "MENU"

    def play_mode(self):
        self.board.reset()
        self.current_player = random.choice([1,2])
        self.game_over = False
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = "MENU"
                        return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.current_player == 2:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        col = self.display.get_column_from_mouse(mouse_x)
                        if col != -1 and self.board.is_valid_move(col):
                            row = self.board.make_move(col, self.current_player)
                            if self.board.check_winner(self.current_player, row, col):
                                self.game_over = True
                                winner = self.current_player
                            elif self.board.is_full():
                                self.game_over = True
                                winner = 0
                            else:
                                self.current_player = 1
            if self.current_player == 1 and not self.game_over:
                valid_moves = self.board.get_valid_moves()
                if valid_moves:
                    state = self.board.get_board_state()
                    col = self.agent.act(state, valid_moves)
                    row = self.board.make_move(col, self.current_player)
                    if self.board.check_winner(self.current_player, row, col):
                        self.game_over = True
                        winner = self.current_player
                    elif self.board.is_full():
                        self.game_over = True
                        winner = 0
                    else:
                        self.current_player = 2
            self.screen.fill((0, 0, 0))
            self.display.draw_board(self.board.board)
            if self.current_player == 1 and not self.game_over:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                col = self.display.get_column_from_mouse(mouse_x)
                if col != -1 and self.board.is_valid_move(col):
                    self.display.draw_piece_preview(col, self.current_player)
            pygame.display.flip()
            self.clock.tick(60)
        self.display.draw_game_over_screen(winner)
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                        waiting = False
                        self.state = "MENU"

    def model_management_menu(self):
        models = self.model_manager.list_saved_models()
        selected_model = 0
        while self.state == "MODEL_MANAGEMENT":
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_model = (selected_model - 1) % len(models)
                    elif event.key == pygame.K_DOWN:
                        selected_model = (selected_model + 1) % len(models)
                    elif event.key == pygame.K_DELETE:
                        if models:
                            self.model_manager.delete_model(models[selected_model]['name'])
                            models.pop(selected_model)
                            if selected_model >= len(models):
                                selected_model = len(models) - 1
                    elif event.key == pygame.K_RETURN:
                        # Load selected model
                        if models:
                            self.agent.load_model(models[selected_model]['path'])
                            self.state = "MENU"
                            break
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "MENU"
                        break
            self.screen.fill((0, 0, 0))
            font = pygame.font.Font(None, 48)
            title = font.render("Saved Models", True, (255, 255, 255))
            self.screen.blit(title, (250, 50))
            if models:
                model_font = pygame.font.Font(None, 36)
                for i, model in enumerate(models):
                    color = (255, 255, 0) if i == selected_model else (255, 255, 255)
                    text = model_font.render(f"{model['name']} - {model['date']}", True, color)
                    self.screen.blit(text, (200, 150 + i * 50))
            else:
                no_models_font = pygame.font.Font(None, 36)
                no_models_text = no_models_font.render("No saved models", True, (255, 255, 255))
                self.screen.blit(no_models_text, (250, 200))
            instruction_font = pygame.font.Font(None, 24)
            up_text = instruction_font.render("UP/DOWN: Navigate", True, (200, 200, 200))
            delete_text = instruction_font.render("DELETE: Remove Model", True, (200, 200, 200))
            enter_text = instruction_font.render("ENTER: Load Model", True, (200, 200, 200))
            esc_text = instruction_font.render("ESC: Return to Menu", True, (200, 200, 200))
            self.screen.blit(up_text, (50, 500))
            self.screen.blit(delete_text, (50, 525))
            self.screen.blit(enter_text, (50, 550))
            self.screen.blit(esc_text, (50, 575))
            pygame.display.flip()
            self.clock.tick(60)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if self.state == "MENU":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
                        elif event.key == pygame.K_DOWN:
                            self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
                        elif event.key == pygame.K_RETURN:
                            if self.menu_selection == 0:
                                self.state = "TRAINING"
                                self.load_existing = False
                            elif self.menu_selection == 1:
                                self.state = "TRAINING"
                                self.load_existing = True
                            elif self.menu_selection == 2:
                                self.state = "PLAYING"
                            elif self.menu_selection == 3:
                                self.state = "MODEL MANAGEMENT"
                            elif self.menu_selection == 4:
                                pygame.quit()
                                sys.exit()
            if self.state == "MENU":
                self.screen.fill((0, 0, 0))
                self.display.draw_menu(self.menu_options, self.menu_selection)
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = GameManager()
    game.run()