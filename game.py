import tkinter as tk
import random

class CyberpunkCoinRain:
    def __init__(self, root):
        self.root = root
        self.root.title("Neon Rain - Cyberpunk Arcade")
        
        # --- FULLSCREEN SETUP ---
        self.root.attributes('-fullscreen', True)
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        self.root.configure(bg="#050814")

        # Controls Binding
        self.root.bind("<Escape>", lambda e: self.toggle_fullscreen())
        self.root.bind("<Left>", lambda e: self.move_player(-55))
        self.root.bind("<Right>", lambda e: self.move_player(55))
        self.root.bind("a", lambda e: self.move_player(-55))
        self.root.bind("d", lambda e: self.move_player(55))

        self.score = 0
        self.high_score = 0
        self.time_left = 35
        self.game_running = True
        self.timer_job = None
        self.game_loop_job = None

        # --- TOP NEON HEADER BAR ---
        self.header_frame = tk.Frame(root, bg="#0d111d", pady=12)
        self.header_frame.pack(fill="x")

        self.lbl_score = tk.Label(
            self.header_frame, 
            text="🪙 SCORE: 0", 
            font=("Consolas", 18, "bold"), 
            bg="#0d111d", 
            fg="#facc15"
        )
        self.lbl_score.pack(side="left", padx=40)

        self.lbl_high = tk.Label(
            self.header_frame, 
            text="🏆 HIGH SCORE: 0", 
            font=("Consolas", 14, "bold"), 
            bg="#0d111d", 
            fg="#a855f7"
        )
        self.lbl_high.pack(side="left", padx=20)

        self.lbl_title = tk.Label(
            self.header_frame, 
            text="✨ CYBER COIN RAIN ✨", 
            font=("Segoe UI", 16, "bold"), 
            bg="#0d111d", 
            fg="#38bdf8"
        )
        self.lbl_title.pack(side="left", expand=True)

        self.lbl_timer = tk.Label(
            self.header_frame, 
            text="⏳ TIME: 35s", 
            font=("Consolas", 18, "bold"), 
            bg="#0d111d", 
            fg="#f43f5e"
        )
        self.lbl_timer.pack(side="right", padx=40)

        # --- CANVAS ARENA ---
        self.canvas_h = self.screen_h - 150
        self.canvas = tk.Canvas(
            root, 
            width=self.screen_w, 
            height=self.canvas_h, 
            bg="#0a0e1a", 
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        # Background Starfield Effect
        self.draw_starfield()

        # Neon Player Paddle (Glow Effect)
        self.p_width = 160
        self.p_height = 24
        self.p_x = (self.screen_w // 2) - (self.p_width // 2)
        self.p_y = self.canvas_h - 55

        # Paddle Outer Glow + Inner Box
        self.paddle_glow = self.canvas.create_rectangle(
            self.p_x - 4, self.p_y - 4, self.p_x + self.p_width + 4, self.p_y + self.p_height + 4,
            fill="#0284c7", outline="", tag="player"
        )
        self.player = self.canvas.create_rectangle(
            self.p_x, self.p_y, self.p_x + self.p_width, self.p_y + self.p_height,
            fill="#38bdf8", outline="#e0f2fe", width=2, tag="player"
        )

        # Falling Items
        self.items = []
        self.create_falling_items()

        # --- BOTTOM CONTROL BAR ---
        self.bottom_frame = tk.Frame(root, bg="#0d111d", pady=10)
        self.bottom_frame.pack(fill="x")

        tk.Button(
            self.bottom_frame,
            text="🔄 Restart Game",
            font=("Segoe UI", 11, "bold"),
            bg="#10b981", fg="white", activebackground="#059669", bd=0, padx=22, pady=6,
            cursor="hand2", command=self.restart_game
        ).pack(side="left", padx=30)

        tk.Label(
            self.bottom_frame,
            text="Controls: ⬅️ ➡️ Arrow Keys / A D | 'ESC' to exit Fullscreen",
            font=("Segoe UI", 11), bg="#0d111d", fg="#64748b"
        ).pack(side="left", expand=True)

        tk.Button(
            self.bottom_frame,
            text="❌ Exit Game",
            font=("Segoe UI", 11, "bold"),
            bg="#f43f5e", fg="white", activebackground="#be123c", bd=0, padx=22, pady=6,
            cursor="hand2", command=self.root.destroy
        ).pack(side="right", padx=30)

        # Start Game
        self.update_game()
        self.update_timer()

    def draw_starfield(self):
        # Decorative stars on canvas background
        for _ in range(70):
            sx = random.randint(10, self.screen_w - 10)
            sy = random.randint(10, self.canvas_h - 10)
            size = random.choice([1, 2, 3])
            color = random.choice(["#1e293b", "#334155", "#475569", "#0284c7"])
            self.canvas.create_oval(sx, sy, sx + size, sy + size, fill=color, outline="")

    def create_falling_items(self):
        # 5 items placed sequentially
        types = ["gold", "gold", "diamond", "bomb", "gold"]
        for i in range(5):
            itype = types[i]
            x = random.randint(80, self.screen_w - 100)
            y = -120 - (i * 190)  # Smooth spacing
            speed = random.randint(4, 7)  # Perfect Speed Range

            item_data = {"type": itype, "x": x, "y": y, "speed": speed, "ids": []}

            if itype == "gold":
                # Shiny 3D Gold Coin
                o1 = self.canvas.create_oval(x, y, x + 30, y + 30, fill="#f59e0b", outline="#fef08a", width=2)
                o2 = self.canvas.create_oval(x + 7, y + 7, x + 23, y + 23, fill="#facc15", outline="")
                item_data["ids"] = [o1, o2]

            elif itype == "diamond":
                # Glowing Neon Diamond
                d = self.canvas.create_polygon(
                    x+16, y, x+32, y+16, x+16, y+32, x, y+16, 
                    fill="#38bdf8", outline="#f0f9ff", width=2
                )
                item_data["ids"] = [d]

            else: # Bomb with fuse spark
                b1 = self.canvas.create_oval(x, y + 4, x + 28, y + 32, fill="#1e293b", outline="#f43f5e", width=2)
                b2 = self.canvas.create_oval(x + 10, y - 2, x + 18, y + 6, fill="#f97316", outline="") # Fuse spark
                item_data["ids"] = [b1, b2]

            self.items.append(item_data)

    def move_player(self, dx):
        if not self.game_running:
            return
        self.p_x = max(20, min(self.screen_w - self.p_width - 20, self.p_x + dx))
        
        # Move both inner box and outer glow
        self.canvas.coords(self.player, self.p_x, self.p_y, self.p_x + self.p_width, self.p_y + self.p_height)
        self.canvas.coords(self.paddle_glow, self.p_x - 4, self.p_y - 4, self.p_x + self.p_width + 4, self.p_y + self.p_height + 4)

    def show_floating_text(self, x, y, text, color):
        t_id = self.canvas.create_text(x, y, text=text, fill=color, font=("Consolas", 16, "bold"))
        
        # Simple upward float animation
        def animate(step=0):
            if step < 5:
                self.canvas.move(t_id, 0, -3)
                self.root.after(50, lambda: animate(step + 1))
            else:
                self.canvas.delete(t_id)
        animate()

    def update_game(self):
        if not self.game_running:
            return

        for item in self.items:
            item["y"] += item["speed"]
            x, y = item["x"], item["y"]

            # Redraw/Move multi-part item shapes
            if item["type"] == "gold":
                self.canvas.coords(item["ids"][0], x, y, x + 30, y + 30)
                self.canvas.coords(item["ids"][1], x + 7, y + 7, x + 23, y + 23)
            elif item["type"] == "diamond":
                self.canvas.coords(item["ids"][0], x+16, y, x+32, y+16, x+16, y+32, x, y+16)
            else: # Bomb
                self.canvas.coords(item["ids"][0], x, y + 4, x + 28, y + 32)
                self.canvas.coords(item["ids"][1], x + 10, y - 2, x + 18, y + 6)

            # Collision Check
            if (self.p_x < x + 30 and 
                self.p_x + self.p_width > x and 
                self.p_y < y + 30 and 
                self.p_y + self.p_height > y):

                if item["type"] == "gold":
                    self.score += 10
                    self.show_floating_text(x, y, "+10 🪙", "#facc15")
                elif item["type"] == "diamond":
                    self.score += 25
                    self.show_floating_text(x, y, "+25 💎", "#38bdf8")
                elif item["type"] == "bomb":
                    self.score = max(0, self.score - 15)
                    self.show_floating_text(x, y, "-15 💥", "#f43f5e")

                self.lbl_score.config(text=f"🪙 SCORE: {self.score}")
                self.reset_item(item)

            elif item["y"] > self.canvas_h:
                self.reset_item(item)

        self.game_loop_job = self.root.after(25, self.update_game)

    def reset_item(self, item):
        item["x"] = random.randint(80, self.screen_w - 100)
        item["y"] = random.randint(-350, -80)
        item["speed"] = random.randint(4, 7)  # Speed tuned

    def update_timer(self):
        if not self.game_running:
            return

        if self.time_left > 0:
            self.lbl_timer.config(text=f"⏳ TIME: {self.time_left}s")
            self.time_left -= 1
            self.timer_job = self.root.after(1000, self.update_timer)
        else:
            self.game_over()

    def game_over(self):
        self.game_running = False
        self.lbl_timer.config(text="⏳ TIME: 0s")

        if self.score > self.high_score:
            self.high_score = self.score
            self.lbl_high.config(text=f"🏆 HIGH SCORE: {self.high_score}")

        cx, cy = self.screen_w // 2, self.canvas_h // 2
        self.canvas.create_rectangle(cx - 270, cy - 130, cx + 270, cy + 130, fill="#0d111d", outline="#38bdf8", width=3, tag="gameover")
        self.canvas.create_text(cx, cy - 65, text="🎮 GAME OVER", fill="#facc15", font=("Segoe UI", 28, "bold"), tag="gameover")
        self.canvas.create_text(cx, cy - 10, text=f"Final Score: {self.score} Points", fill="white", font=("Segoe UI", 20, "bold"), tag="gameover")
        self.canvas.create_text(cx, cy + 35, text=f"High Score: {self.high_score} Points", fill="#a855f7", font=("Segoe UI", 14, "bold"), tag="gameover")
        self.canvas.create_text(cx, cy + 80, text="Click 'Restart Game' to play again!", fill="#94a3b8", font=("Segoe UI", 12), tag="gameover")

    def toggle_fullscreen(self):
        is_full = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not is_full)

    def restart_game(self):
        if self.timer_job: self.root.after_cancel(self.timer_job)
        if self.game_loop_job: self.root.after_cancel(self.game_loop_job)

        self.canvas.delete("gameover")
        self.score = 0
        self.time_left = 35
        self.game_running = True

        self.p_x = (self.screen_w // 2) - (self.p_width // 2)
        self.canvas.coords(self.player, self.p_x, self.p_y, self.p_x + self.p_width, self.p_y + self.p_height)
        self.canvas.coords(self.paddle_glow, self.p_x - 4, self.p_y - 4, self.p_x + self.p_width + 4, self.p_y + self.p_height + 4)

        self.lbl_score.config(text="🪙 SCORE: 0")
        self.lbl_timer.config(text="⏳ TIME: 35s")

        for i, item in enumerate(self.items):
            item["x"] = random.randint(80, self.screen_w - 100)
            item["y"] = -120 - (i * 190)
            item["speed"] = random.randint(4, 7)

        self.update_game()
        self.update_timer()

if __name__ == "__main__":
    root = tk.Tk()
    app = CyberpunkCoinRain(root)
    root.mainloop()