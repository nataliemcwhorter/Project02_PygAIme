import random
import pygame
import sys
from ai.training import TrainingManager
from game.board import Connect4Board
from ai.q_agent import QAgent
from game.display import Connect4Display
from utils.file_manager import ModelManager

"""
Connect4Game is a reinforcement learning project that allows you to play connect4 againt an ai
__author__ = "nataliemcwhorter"
__version__ = "10.27.2025"
"""
class GameManager:
    """
    initializes the game manager (main class)
    """
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption('Connect 4 AI')
        self.clock = pygame.time.Clock()
        self.board = Connect4Board()
        self.display = Connect4Display(self.screen)
        self.agent = QAgent()
        self.model_manager = ModelManager()
        self.trainer = TrainingManager(self.agent, self.board)
        self.state = 'MENU'
        self.menu_options = ['Train New Model', 'Load Existing Model', 'Play vs AI', 'Manage Models', 'Quit']
        self.menu_selection = 0
        self.current_player = 1
        self.game_over = False
        self.load_existing = False
        self.selected_model_index = 0
        self.x=0
        self.model_name_choice = "untrained model"

    """
    run() runs the game loop
    calls methods from other classes to perform
    """
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if self.state == 'MENU':
                    self.handle_menu_events(event)
                elif self.state == 'TRAINING':
                    self.handle_training_events(event)
                elif self.state == 'PLAYING':
                    self.handle_play_events(event)
                elif self.state == 'MODEL MANAGEMENT':
                    self.handle_model_management_events(event)
            if self.state == 'MENU':
                self.screen.fill((0, 0, 0))
                self.display.draw_menu(self.menu_options, self.menu_selection)
            elif self.state == 'TRAINING':
                self.training_mode()
            elif self.state == 'PLAYING':
                self.play_mode()
            elif self.state == 'MODEL MANAGEMENT':
                self.model_management_menu()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()

    """
    handle_menu_events(self, event) handles user selection from menu options
    event is feedback from the keyboard event item
    """
    def handle_menu_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
            elif event.key == pygame.K_DOWN:
                self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
            elif event.key == pygame.K_RETURN:
                if self.menu_selection == 0:
                    self.state = 'TRAINING'
                    self.load_existing = False
                elif self.menu_selection == 1:
                    self.state = 'TRAINING'
                    self.load_existing = True
                elif self.menu_selection == 2:
                    self.state = 'PLAYING'
                elif self.menu_selection == 3:
                    self.state = 'MODEL MANAGEMENT'
                elif self.menu_selection == 4:
                    pygame.quit()
                    sys.exit()

    """
    handle_training_events(self, event) handles user selection from training mode
    event is feedback from the keyboard event item
    """
    def handle_training_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = 'MENU'
            elif event.key == pygame.K_s:
                self.save_training_model()

    """
    save_training_model(self, model) saves the model
    model is the specified model that is to be saved
    """
    def save_training_model(self):
        self.display.draw_save_prompt()
        pygame.display.flip()
        waiting_for_save = True
        while waiting_for_save:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        model_name = self.model_manager.generate_model_name(self.model_name_choice)
                        metadata = {'episode': self.trainer.training_stats['total_episodes'],
                                'win_rate': self.trainer.get_training_progress()['win_rate']}
                        self.model_manager.save_model(
                            self.agent,
                            model_name,
                            {
                                'episode': self.trainer.training_stats['total_episodes'],
                                'win_rate': self.trainer.get_training_progress()['win_rate']
                            }
                        )
                        self.model_manager.save_metadata(model_name, metadata)
                        self.trainer.initialize(model_name)
                        waiting_for_save = False
                    elif event.key == pygame.K_n:
                        waiting_for_save = False

    """
    training_mode(self) handles the different training options
    """
    def training_mode(self):
        if self.load_existing:
            saved_models = self.model_manager.list_saved_models()
            if saved_models:
                selecting = True
                while selecting:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_UP:
                                self.selected_model_index = (self.selected_model_index - 1) % len(saved_models)
                            elif event.key == pygame.K_DOWN:
                                self.selected_model_index = (self.selected_model_index + 1) % len(saved_models)
                            elif event.key == pygame.K_RETURN:
                                fp = saved_models[self.selected_model_index][0]
                                self.agent.load_model(fp)
                                selecting = False
                            elif event.key == pygame.K_ESCAPE:
                                self.state = 'MENU'
                                return
                    self.screen.fill((0, 0, 0))
                    font = pygame.font.Font(None, 36)
                    title = font.render('Select Model to Load', True, (255, 255, 255))
                    self.screen.blit(title, (250, 50))
                    for i, model in enumerate(saved_models):
                        color = (255, 255, 0) if i == self.selected_model_index else (255, 255, 255)
                        text = font.render(f"Model {i}: {model}", True, color)
                        self.screen.blit(text, (250, 150 + i * 50))
                    pygame.display.flip()
            else:
                self.load_existing = False
        if not self.load_existing:
            self.agent = QAgent()  # Fresh agent
        training_modes = ['Self Play', 'vs Random', 'vs Human', 'Back to Menu']
        mode_selection = 0
        selecting_mode = True
        while selecting_mode:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        mode_selection = (mode_selection - 1) % len(training_modes)
                    elif event.key == pygame.K_DOWN:
                        mode_selection = (mode_selection + 1) % len(training_modes)
                    elif event.key == pygame.K_RETURN:
                        if mode_selection == 0:
                            training_stats = self._train_with_display(mode='self_play', episodes=1)
                            selecting_mode = False
                        elif mode_selection == 1:
                            training_stats = self._train_with_display(mode='vs_random', episodes=1)
                            selecting_mode = False
                        elif mode_selection == 2:
                            training_stats = self._train_with_human_display()
                            print(training_stats)
                            selecting_mode = False
                        elif mode_selection == 3:
                            self.state = 'MENU'
                            return
                    elif event.key == pygame.K_ESCAPE:
                        self.state = 'MENU'
                        return
            self.screen.fill((0, 0, 0))
            font = pygame.font.Font(None, 36)
            title = font.render('Select Training Mode', True, (255, 255, 255))
            self.screen.blit(title, (250, 50))
            for i, mode in enumerate(training_modes):
                color = (255, 255, 0) if i == mode_selection else (255, 255, 255)
                text = font.render(mode, True, color)
                self.screen.blit(text, (250, 150 + i * 50))
            pygame.display.flip()
        model_name = self.model_manager.generate_model_name(self.model_name_choice)
        self.model_manager.save_model(
            self.agent,
            model_name,
            {
                'episodes': training_stats['total_episodes'],
                'win_rate': training_stats['win_rate'],
                'final_epsilon': training_stats.get('final_epsilon', 0)
            }
        )
        self.model_manager.save_metadata(model_name, training_stats)
        self.state = 'MENU'

    """
    _train_with_display(self, mode, episodes) creates the display for while training
    mode is the type of training mode
    episodes is the number of training episodes
    """
    def _train_with_display(self, mode, episodes):
        font = pygame.font.Font(None, 36)
        training_stats = self.trainer.train(mode=mode, episodes=episodes)
        self.screen.fill((0, 0, 0))
        title = font.render('Training Complete', True, (255, 255, 255))
        win_rate_text = font.render(f'Win Rate: {training_stats["win_rate"]:.2f}', True, (255, 255, 255))
        episodes_text = font.render(f'Episodes: {training_stats["episodes"]}', True, (255, 255, 255))
        self.screen.blit(title, (250, 200))
        self.screen.blit(win_rate_text, (250, 250))
        self.screen.blit(episodes_text, (250, 300))
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        waiting = False
        return training_stats

    """
    _train_with_human_display(self) creates the display for while training with human
    """
    def _train_with_human_display(self):
        """
        human_move_callback(valid_moves) finds the move that the human does
        """
        def human_move_callback(valid_moves):
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        col = self.display.get_column_from_mouse(mouse_x)
                        if col in valid_moves:
                            return col
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.state = 'MENU'
                            return -1  # Indicate exit

                # Draw the current board state
                self.screen.fill((0, 0, 0))
                self.display.draw_board(self.board.board)
                pygame.display.flip()

        # Prepare for human training
        font = pygame.font.Font(None, 36)

        # Prepare display
        self.screen.fill((0, 0, 0))
        title = font.render('Human Training Mode', True, (255, 255, 255))
        instruction1 = font.render('Click columns to make moves', True, (255, 255, 255))
        instruction2 = font.render('AI will learn from your gameplay', True, (255, 255, 255))

        self.screen.blit(title, (250, 200))
        self.screen.blit(instruction1, (250, 250))
        self.screen.blit(instruction2, (250, 300))

        pygame.display.flip()

        # Wait for user to be ready
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        waiting = False

        # Tracking training progress
        training_stats = {
            'episodes': 0,
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'win_rate': 0.0,
            'total_episodes': self.trainer.training_stats['total_episodes']
        }

        # Training loop
        training_active = True
        while training_active:
            # Pass the callback to the training method
            try:
                current_game_stats = self.trainer.train(
                    mode='vs_human',
                    human_move_callback=human_move_callback
                )
                print(current_game_stats)

                # Update overall training stats
                training_stats['episodes'] += current_game_stats['episodes']
                training_stats['wins'] += current_game_stats['wins']
                training_stats['losses'] += current_game_stats['losses']
                training_stats['draws'] += current_game_stats['draws']
                training_stats['win_rate'] = training_stats['wins'] / training_stats['episodes']
                training_stats['total_episodes'] += current_game_stats['episodes']
                print(training_stats)
            except Exception as e:
                print(f"Training error: {e}")
                self.state = 'MENU'
                return training_stats

            # Training complete screen
            self.screen.fill((0, 0, 0))

            # Display training results
            title = font.render('Training Round Complete', True, (255, 255, 255))
            win_rate_text = font.render(f'Win Rate: {training_stats["win_rate"]:.2f}', True, (255, 255, 255))
            episodes_text = font.render(f'Total Episodes: {training_stats["episodes"]}', True, (255, 255, 255))

            continue_text = font.render('Press SPACE to continue training', True, (200, 200, 200))
            exit_text = font.render('Press ESC to exit', True, (200, 200, 200))

            self.screen.blit(title, (250, 200))
            self.screen.blit(win_rate_text, (250, 250))
            self.screen.blit(episodes_text, (250, 300))
            self.screen.blit(continue_text, (250, 400))
            self.screen.blit(exit_text, (250, 450))

            pygame.display.flip()

            # Wait for user to continue or exit
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                            waiting = False
                            break
                        elif event.key == pygame.K_ESCAPE:
                            training_active = False
                            waiting= False
                            break
        return training_stats

    """
    play_mode(self) creates the display for when playing against the model
    """
    def play_mode(self):
        if self.x ==0:
            # FIRST: Select which model to play against
            saved_models = self.model_manager.list_saved_models()

            if not saved_models:
                # Show error - no trained models available
                font = pygame.font.Font(None, 36)
                self.screen.fill((0, 0, 0))
                error_text = font.render('No trained models found!', True, (255, 0, 0))
                instruction = font.render('Train a model first', True, (255, 255, 255))
                self.screen.blit(error_text, (250, 250))
                self.screen.blit(instruction, (250, 300))
                pygame.display.flip()
                # Wait for keypress then return to menu
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            self.state = 'MENU'
                            return
                return
            # Show model selection menu (similar to your training_mode logic)
            selecting = True
            selected_model_index = 0
            while selecting:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            selected_model_index = (selected_model_index - 1) % len(saved_models)
                        elif event.key == pygame.K_DOWN:
                            selected_model_index = (selected_model_index + 1) % len(saved_models)
                        elif event.key == pygame.K_RETURN:
                            # Load the selected model
                            model_path = saved_models[selected_model_index][0]
                            self.agent.load_model(model_path)
                            selecting = False
                        elif event.key == pygame.K_ESCAPE:
                            self.state = 'MENU'
                            return
                # Draw model selection screen
                self.screen.fill((0, 0, 0))
                font = pygame.font.Font(None, 36)
                title = font.render('Select AI Opponent', True, (255, 255, 255))
                self.screen.blit(title, (250, 50))
                for i, model in enumerate(saved_models):
                    color = (255, 255, 0) if i == selected_model_index else (255, 255, 255)
                    text = font.render(f"Model {i}: {model[0]}", True, color)
                    self.screen.blit(text, (250, 150 + i * 50))
                pygame.display.flip()
                self.x = self.x + 1

        self.board.reset()
        self.current_player = random.choice([1,2])  # Human starts
        self.game_over = False

        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = 'MENU'
                        return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.current_player == 1:  # Human player
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        col = self.display.get_column_from_mouse(mouse_x)
                        if col != -1 and self.board.is_valid_move(col):
                            row = self.board.make_move(col, self.current_player)
                            if self.board.check_winner(self.current_player, row, col):
                                self.game_over = True
                                winner = self.current_player
                            elif self.board.is_full():
                                self.game_over = True
                                winner = 0  # Tie
                            else:
                                self.current_player = 2  # Switch to AI

            # AI turn
            if self.current_player == 2 and not self.game_over:
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
                        winner = 0  # Tie
                    else:
                        self.current_player = 1  # Switch back to human

            # Draw everything
            self.screen.fill((0, 0, 0))
            self.display.draw_board(self.board.board)

            # Show piece preview for human player
            if self.current_player == 1 and not self.game_over:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                col = self.display.get_column_from_mouse(mouse_x)
                if col != -1 and self.board.is_valid_move(col):
                    self.display.draw_piece_preview(col, self.current_player)

            pygame.display.flip()
            self.clock.tick(60)

        # Game over - show result
        self.display.draw_game_over_screen(winner)
        pygame.display.flip()

        # Wait for user to continue
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        # Reset board and continue training
                        self.board.reset()
                        self.current_player = random.choice([1,2])
                        self.game_over = False

                        # Update AI's knowledge based on the game
                        if winner == 1:  # Human won
                            self.agent.replay()
                            reward = 100
                        elif winner == 2:  # AI won
                            self.agent.replay()
                            reward = -100
                        else:  # Tie
                            self.agent.replay()
                            reward = 0

                        # Optional: Update target network
                        self.agent.update_target_network()

                        waiting = False
                    elif event.key == pygame.K_ESCAPE:
                        self.state = 'MENU'
                        self.x = 0
                        waiting = False

    """
    model_management_menu(self) creates the menu for managing different models
    """
    def model_management_menu(self):
        models = self.model_manager.list_saved_models()
        selected_model = 0
        while self.state == 'MODEL MANAGEMENT':
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
                        if models:
                            m = models[selected_model][0]
                            self.agent.load_model(m)
                            self.state = 'MENU'
                            break
                    elif event.key == pygame.K_ESCAPE:
                        self.state = 'MENU'
                        break
            self.screen.fill((0, 0, 0))
            font = pygame.font.Font(None, 48)
            title = font.render('Saved Models', True, (255, 255, 255))
            self.screen.blit(title, (250, 50))
            if models:
                model_font = pygame.font.Font(None, 36)
                for i, model in enumerate(models):
                    color = (255, 255, 0) if i == selected_model else (255, 255, 255)
                    text = model_font.render(f"Model {i}: {model}", True, color)
                    self.screen.blit(text, (200, 150 + i * 50))
            else:
                no_models_font = pygame.font.Font(None, 36)
                no_models_text = no_models_font.render('No saved models', True, (255, 255, 255))
                self.screen.blit(no_models_text, (250, 200))
            instruction_font = pygame.font.Font(None, 24)
            up_text = instruction_font.render('UP/DOWN: Navigate', True, (200, 200, 200))
            delete_text = instruction_font.render('DELETE: Remove Model', True, (200, 200, 200))
            enter_text = instruction_font.render('ENTER: Load Model', True, (200, 200, 200))
            esc_text = instruction_font.render('ESC: Return to Menu', True, (200, 200, 200))
            self.screen.blit(up_text, (50, 500))
            self.screen.blit(delete_text, (50, 525))
            self.screen.blit(enter_text, (50, 550))
            self.screen.blit(esc_text, (50, 575))
            pygame.display.flip()
            self.clock.tick(60)

    def handle_play_events(self, event):
        pass

    def handle_model_management_events(self, event):
        pass

if __name__ == '__main__':
    game = GameManager()
    game.run()