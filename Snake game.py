import tkinter as tk
import random
from collections import deque

class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🐍 Snake Game 🐍")
        
        # Get screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Game settings - fullscreen by default
        self.canvas_width = self.screen_width
        self.canvas_height = self.screen_height - 50  # Leave room for label
        self.grid_size = 20
        self.grid_width = self.canvas_width // self.grid_size
        self.grid_height = self.canvas_height // self.grid_size
        
        # Fullscreen state
        self.is_fullscreen = False
        self.toggle_fullscreen()
        
        self.root.resizable(False, False)
        
        # Colors
        self.colors = {
            'bg': '#1a1a2e',
            'grid': '#16213e',
            'snake_head': '#00ff00',
            'snake_body': '#00cc00',
            'food': '#ff6b00',
            'menu_bg': '#0f3460',
        }
        
        # Create canvas
        self.canvas = tk.Canvas(
            root, 
            width=self.canvas_width, 
            height=self.canvas_height,
            bg=self.colors['bg'],
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Score label
        self.score_label = tk.Label(root, text="Score: 0", font=("Arial", 14), fg="yellow", bg=self.colors['bg'])
        self.score_label.pack()
        
        # Initialize enemy snake BEFORE reset_game
        self.enemy_snake = None
        self.enemy_direction = 'UP'
        
        self.state = 'MENU'  # MENU, PLAYING, PAUSED, GAME_OVER
        self.reset_game()
        self.draw_menu()
        
        # Bind keys
        self.root.bind('<KeyPress>', self.handle_key)
        self.root.bind('<Up>', lambda e: self.set_direction('UP'))
        self.root.bind('<Down>', lambda e: self.set_direction('DOWN'))
        self.root.bind('<Left>', lambda e: self.set_direction('LEFT'))
        self.root.bind('<Right>', lambda e: self.set_direction('RIGHT'))
        self.root.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.root.bind('<Escape>', lambda e: self.toggle_fullscreen() if self.is_fullscreen else None)
    
    def reset_game(self):
        start_x = self.grid_width // 2
        start_y = self.grid_height // 2
        self.snake = deque([
            (start_x, start_y),
            (start_x - 1, start_y),
            (start_x - 2, start_y)
        ])
        self.direction = 'RIGHT'
        self.next_direction = 'RIGHT'
        self.apple = self.spawn_apple()
        self.score = 0
        
        # Reset enemy snake when game restarts
        self.enemy_snake = None
        self.enemy_direction = 'UP'
    
    def spawn_apple(self):
        while True:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            if (x, y) not in self.snake and (self.enemy_snake is None or (x, y) not in self.enemy_snake):
                return (x, y)
    
    def spawn_enemy(self):
        """Spawn enemy snake when score reaches 100"""
        if self.score >= 100 and self.enemy_snake is None:
            enemy_x = random.randint(0, self.grid_width - 1)
            enemy_y = random.randint(0, self.grid_height - 1)
            # Make sure enemy doesn't spawn on player
            while (enemy_x, enemy_y) in self.snake or abs(enemy_x - self.snake[0][0]) < 3:
                enemy_x = random.randint(0, self.grid_width - 1)
                enemy_y = random.randint(0, self.grid_height - 1)
            
            self.enemy_snake = deque([
                (enemy_x, enemy_y),
                (enemy_x - 1, enemy_y),
                (enemy_x - 2, enemy_y)
            ])
            self.enemy_direction = 'UP'
    
    def get_enemy_direction(self):
        """AI: Make enemy follow player"""
        if self.enemy_snake is None:
            return
        
        enemy_head = self.enemy_snake[0]
        player_head = self.snake[0]
        
        # Calculate difference
        dx = player_head[0] - enemy_head[0]
        dy = player_head[1] - enemy_head[1]
        
        # Determine best direction to follow player
        if abs(dx) > abs(dy):
            if dx > 0:
                new_dir = 'RIGHT'
            else:
                new_dir = 'LEFT'
        else:
            if dy > 0:
                new_dir = 'DOWN'
            else:
                new_dir = 'UP'
        
        # Don't reverse into itself
        opposite = {'UP': 'DOWN', 'DOWN': 'UP', 'LEFT': 'RIGHT', 'RIGHT': 'LEFT'}
        if new_dir != opposite.get(self.enemy_direction):
            self.enemy_direction = new_dir
    
    def set_direction(self, direction):
        if self.state == 'PLAYING':
            if direction == 'UP' and self.direction != 'DOWN':
                self.next_direction = 'UP'
            elif direction == 'DOWN' and self.direction != 'UP':
                self.next_direction = 'DOWN'
            elif direction == 'LEFT' and self.direction != 'RIGHT':
                self.next_direction = 'LEFT'
            elif direction == 'RIGHT' and self.direction != 'LEFT':
                self.next_direction = 'RIGHT'
    
    def handle_key(self, event):
        if event.keysym == 'space':
            if self.state == 'MENU':
                self.start_game()
            elif self.state == 'GAME_OVER':
                self.state = 'MENU'
                self.draw_menu()
        elif event.keysym == 'p':
            if self.state == 'PLAYING':
                self.state = 'PAUSED'
                self.draw_pause()
            elif self.state == 'PAUSED':
                self.state = 'PLAYING'
                self.update_game()
    
    def start_game(self):
        self.state = 'PLAYING'
        self.reset_game()
        self.update_game()
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)
        if self.is_fullscreen:
            self.root.config(cursor="none")
        else:
            self.root.config(cursor="arrow")
    
    def update_game(self):
        if self.state != 'PLAYING':
            return
        
        self.direction = self.next_direction
        
        # Calculate new head position with wraparound
        head_x, head_y = self.snake[0]
        directions = {
            'UP': (0, -1),
            'DOWN': (0, 1),
            'LEFT': (-1, 0),
            'RIGHT': (1, 0)
        }
        dx, dy = directions[self.direction]
        new_head_x = (head_x + dx) % self.grid_width
        new_head_y = (head_y + dy) % self.grid_height
        new_head = (new_head_x, new_head_y)
        
        # Check collision with self
        if new_head in self.snake:
            self.state = 'GAME_OVER'
            self.draw_game_over()
            return
        
        # Check collision with enemy
        if self.enemy_snake and new_head in self.enemy_snake:
            self.state = 'GAME_OVER'
            self.draw_game_over()
            return
        
        self.snake.appendleft(new_head)
        
        # Check apple collision
        if new_head == self.apple:
            self.score += 10
            self.apple = self.spawn_apple()
        else:
            self.snake.pop()
        
        # Spawn enemy at score 100
        self.spawn_enemy()
        
        # Update enemy
        if self.enemy_snake:
            self.get_enemy_direction()
            
            # Move enemy
            dx, dy = directions[self.enemy_direction]
            enemy_head_x, enemy_head_y = self.enemy_snake[0]
            new_enemy_head_x = (enemy_head_x + dx) % self.grid_width
            new_enemy_head_y = (enemy_head_y + dy) % self.grid_height
            new_enemy_head = (new_enemy_head_x, new_enemy_head_y)
            
            # Enemy collision with self
            if new_enemy_head not in self.enemy_snake:
                self.enemy_snake.appendleft(new_enemy_head)
                self.enemy_snake.pop()
            
            # Enemy eating apples
            if new_enemy_head == self.apple:
                self.apple = self.spawn_apple()
        
        self.draw_game()
        self.root.after(100, self.update_game)
    
    def draw_menu(self):
        self.canvas.delete('all')
        self.canvas.create_rectangle(0, 0, self.canvas_width, self.canvas_height, fill='#00ffff', outline='#00ffff')
        
        # Draw title
        self.canvas.create_text(
            self.canvas_width // 2,
            self.canvas_height // 2 - 100,
            text="🐍 SNAKE GAME 🐍",
            font=("Arial", 72, "bold"),
            fill="yellow"
        )
        
        # Draw instructions
        self.canvas.create_text(
            self.canvas_width // 2,
            self.canvas_height // 2,
            text="Press SPACE to Start",
            font=("Arial", 32),
            fill="white"
        )
        
        self.canvas.create_text(
            self.canvas_width // 2,
            self.canvas_height // 2 + 60,
            text="Arrow Keys to Move | P to Pause | F11 for Fullscreen",
            font=("Arial", 20),
            fill="black"
        )
        
        self.canvas.create_text(
            self.canvas_width // 2,
            self.canvas_height // 2 + 100,
            text="Eat 100 apples to spawn an ENEMY! 👿",
            font=("Arial", 20),
            fill="red"
        )
    
    def draw_game(self):
        self.canvas.delete('all')
        
        # Draw grid
        for x in range(0, self.canvas_width, self.grid_size):
            self.canvas.create_line(x, 0, x, self.canvas_height, fill=self.colors['grid'], width=1)
        for y in range(0, self.canvas_height, self.grid_size):
            self.canvas.create_line(0, y, self.canvas_width, y, fill=self.colors['grid'], width=1)
        
        # Draw player snake
        for i, (x, y) in enumerate(self.snake):
            rect_x = x * self.grid_size
            rect_y = y * self.grid_size
            if i == 0:  # Head
                self.canvas.create_rectangle(
                    rect_x, rect_y,
                    rect_x + self.grid_size, rect_y + self.grid_size,
                    fill=self.colors['snake_head'], outline='white', width=2
                )
                # Draw eye
                self.canvas.create_oval(
                    rect_x + 4, rect_y + 4,
                    rect_x + 8, rect_y + 8,
                    fill='white'
                )
            else:  # Body
                color = self.colors['snake_head'] if i % 2 == 0 else self.colors['snake_body']
                self.canvas.create_rectangle(
                    rect_x, rect_y,
                    rect_x + self.grid_size, rect_y + self.grid_size,
                    fill=color, outline='black', width=1
                )
        
        # Draw enemy snake if exists
        if self.enemy_snake:
            for i, (x, y) in enumerate(self.enemy_snake):
                rect_x = x * self.grid_size
                rect_y = y * self.grid_size
                if i == 0:  # Enemy head
                    self.canvas.create_rectangle(
                        rect_x, rect_y,
                        rect_x + self.grid_size, rect_y + self.grid_size,
                        fill='#ff3333', outline='#ff6666', width=2
                    )
                    # Draw eye
                    self.canvas.create_oval(
                        rect_x + 4, rect_y + 4,
                        rect_x + 8, rect_y + 8,
                        fill='white'
                    )
                else:  # Enemy body
                    self.canvas.create_rectangle(
                        rect_x, rect_y,
                        rect_x + self.grid_size, rect_y + self.grid_size,
                        fill='#cc2222', outline='black', width=1
                    )
        
        # Draw apple
        apple_x, apple_y = self.apple
        rect_x = apple_x * self.grid_size
        rect_y = apple_y * self.grid_size
        self.canvas.create_rectangle(
            rect_x, rect_y,
            rect_x + self.grid_size, rect_y + self.grid_size,
            fill='#ff4444', outline='#ff0000', width=2
        )
        # Draw apple circle inside
        self.canvas.create_oval(
            rect_x + 2, rect_y + 2,
            rect_x + self.grid_size - 2, rect_y + self.grid_size - 2,
            fill='#ff6666', outline='#cc0000', width=1
        )
        
        # Update score
        score_text = f"Score: {self.score}"
        if self.enemy_snake:
            score_text += " | 👿 ENEMY ACTIVE! 👿"
        self.score_label.config(text=score_text)
    
    def draw_pause(self):
        self.canvas.create_rectangle(
            self.canvas_width // 2 - 150,
            self.canvas_height // 2 - 60,
            self.canvas_width // 2 + 150,
            self.canvas_height // 2 + 60,
            fill='black',
            outline='yellow',
            width=3
        )
        self.canvas.create_text(
            self.canvas_width // 2,
            self.canvas_height // 2 - 20,
            text="PAUSED",
            font=("Arial", 32, "bold"),
            fill="yellow"
        )
        self.canvas.create_text(
            self.canvas_width // 2,
            self.canvas_height // 2 + 20,
            text="Press P to Resume",
            font=("Arial", 16),
            fill="white"
        )
    
    def draw_game_over(self):
        self.canvas.create_rectangle(
            0, 0,
            self.canvas_width, self.canvas_height,
            fill='red',
            outline='red'
        )
        
        # Check if enemy caused game over
        player_head = self.snake[0]
        enemy_msg = ""
        if self.enemy_snake and player_head in self.enemy_snake:
            enemy_msg = "😱 "
        
        self.canvas.create_text(
            self.canvas_width // 2,
            self.canvas_height // 2 - 60,
            text=f"{enemy_msg}GAME OVER!",
            font=("Arial", 48, "bold"),
            fill="yellow"
        )
        self.canvas.create_text(
            self.canvas_width // 2,
            self.canvas_height // 2,
            text=f"Final Score: {self.score}",
            font=("Arial", 32),
            fill="cyan"
        )
        self.canvas.create_text(
            self.canvas_width // 2,
            self.canvas_height // 2 + 60,
            text="Press SPACE to Return to Menu",
            font=("Arial", 20),
            fill="white"
        )

if __name__ == "__main__":
    try:
        root = tk.Tk()
        game = SnakeGame(root)
        root.mainloop()
    
