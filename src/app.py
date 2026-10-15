import sys
import json
import threading
import traceback
import webbrowser

from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import pygame
import numpy as np

from board import Board, next_board
from telemetry import Telemetry
from workflow import graph


# ── Display settings ──────────────────────────────────────────────
CELL_SIZE = 20
BOARD_ROWS = 60
BOARD_COLS = 80
WINDOW_W = BOARD_COLS * CELL_SIZE
GRID_H = BOARD_ROWS * CELL_SIZE
BAR_H = 50
WINDOW_H = GRID_H + BAR_H
FPS = 15

# ── Colour palette ────────────────────────────────────────────────
BG        = (10, 10, 18)
CELL_CLR  = (0, 180, 255)
BIRTH_CLR = (0, 255, 130)
CULL_CLR  = (255, 70, 70)
HUD_BG    = (20, 20, 30, 200)
HUD_TEXT  = (200, 220, 255)
BTN_BG    = (30, 30, 45)
BTN_HOVER = (50, 50, 70)
BTN_TEXT  = (200, 220, 255)
BAR_BG    = (15, 15, 25)

# ── AI settings ───────────────────────────────────────────────────
AI_INTERVAL = 50
BOOST_CELLS = 40
CULL_RADIUS = 8
SPORULATION_CELLS = 80


class Engine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption("The Symbiosis Engine")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Consolas", 18)
        self.big_font = pygame.font.SysFont("Consolas", 30, bold=True)

        self.board = Board.from_size(BOARD_ROWS, BOARD_COLS)
        self.board.seed_random(300)
        self.epoch = 0

        self.telemetry = self._connect_telemetry()

        self.ai_decision = ""
        self.ai_reasoning = ""
        self.ai_flash_timer = 0
        self.ai_running = False
        self.highlight_cells: list[tuple[int, int]] = []
        self.highlight_color = BIRTH_CLR
        self.highlight_timer = 0
        self.paused = False

        self.btn_font = pygame.font.SysFont("Consolas", 18, bold=True)
        btn_w, btn_h = 180, 36
        btn_y = GRID_H + (BAR_H - btn_h) // 2
        self.btn_pause = pygame.Rect(10, btn_y, btn_w, btn_h)
        self.btn_langfuse = pygame.Rect(200, btn_y, btn_w, btn_h)

    def _connect_telemetry(self) -> Telemetry | None:
        try:
            t = Telemetry()
            t.clear()
            print("[telemetry] Connected to ClickHouse")
            return t
        except Exception as e:
            print(f"[telemetry] ClickHouse unavailable — running without telemetry: {e}")
            traceback.print_exc()
            return None

    # ── Main loop ─────────────────────────────────────────────────
    def run(self):
        running = True
        while running:
            running = self._handle_events()
            self._update()
            self._render()
            self.clock.tick(FPS)
        pygame.quit()

    def _handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                    print(f"[engine] {'Paused' if self.paused else 'Resumed'}")
                if event.key == pygame.K_r:
                    self.board = Board.from_size(BOARD_ROWS, BOARD_COLS)
                    self.board.seed_random(300)
                    self.epoch = 0
                    if self.telemetry:
                        self.telemetry.clear()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.btn_pause.collidepoint(event.pos):
                    self.paused = not self.paused
                    print(f"[engine] {'Paused' if self.paused else 'Resumed'}")
                elif self.btn_langfuse.collidepoint(event.pos):
                    webbrowser.open("http://localhost:3000")
                    print("[engine] Opened Langfuse dashboard")
        return True

    def _update(self):
        if self.paused:
            return
        self.board.step()
        self.epoch += 1

        if self.telemetry:
            try:
                self.telemetry.record(
                    self.board.grid,
                    ai_decision=self.ai_decision,
                    ai_reasoning=self.ai_reasoning,
                )
            except Exception as e:
                print(f"[telemetry] Record failed: {e}")

        if self.epoch % AI_INTERVAL == 0 and not self.ai_running:
            self._request_ai_decision()

        if self.ai_flash_timer > 0:
            self.ai_flash_timer -= 1
        if self.highlight_timer > 0:
            self.highlight_timer -= 1
        else:
            self.highlight_cells = []

    def _request_ai_decision(self):
        alive = int(self.board.grid.sum())
        total = self.board.grid.size
        density = alive / total

        board_summary = (
            f"Epoch: {self.epoch}\n"
            f"Alive cells: {alive} / {total}\n"
            f"Density: {density:.4f} ({density*100:.1f}%)\n"
            f"Grid: {BOARD_ROWS} x {BOARD_COLS}"
        )

        history_str = "No telemetry history available"
        if self.telemetry:
            try:
                history = self.telemetry.recent_history(10)
                if history:
                    history_str = json.dumps(history, indent=2)
            except Exception as e:
                print(f"[telemetry] History fetch failed: {e}")

        self.ai_running = True
        print(f"[ai] Epoch {self.epoch} — requesting quorum sensing (density: {density*100:.1f}%)")

        def _run():
            try:
                result = graph.invoke({
                    "board_summary": board_summary,
                    "telemetry_history": history_str,
                    "decision": "",
                    "reasoning": "",
                })
                self.ai_decision = result.get("decision", "HOMEOSTASIS")
                self.ai_reasoning = result.get("reasoning", "")
                print(f"[ai] Epoch {self.epoch} → {self.ai_decision}: {self.ai_reasoning}")
                self._apply_decision(self.ai_decision)
                self.ai_flash_timer = FPS * 3
            except Exception as e:
                self.ai_decision = "ERROR"
                self.ai_reasoning = str(e)[:80]
                self.ai_flash_timer = FPS * 3
                print(f"[ai] Error during quorum sensing:")
                traceback.print_exc()
            finally:
                self.ai_running = False

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

    def _apply_decision(self, decision: str):
        grid = self.board.grid
        if decision == "NUTRIENT_BOOST":
            dead_cells = list(zip(*np.where(grid == 0)))
            if dead_cells:
                count = min(BOOST_CELLS, len(dead_cells))
                indices = np.random.choice(len(dead_cells), count, replace=False)
                placed = []
                for i in indices:
                    r, c = dead_cells[i]
                    grid[r, c] = 1
                    placed.append((r, c))
                self.highlight_cells = placed
                self.highlight_color = BIRTH_CLR
                self.highlight_timer = FPS * 2

        elif decision == "PHAGE_CULL":
            alive_positions = list(zip(*np.where(grid == 1)))
            if alive_positions:
                center_idx = np.random.randint(len(alive_positions))
                cr, cc = alive_positions[center_idx]
                culled = []
                for r in range(max(0, cr - CULL_RADIUS), min(BOARD_ROWS, cr + CULL_RADIUS)):
                    for c in range(max(0, cc - CULL_RADIUS), min(BOARD_COLS, cc + CULL_RADIUS)):
                        if grid[r, c] == 1:
                            grid[r, c] = 0
                            culled.append((r, c))
                self.highlight_cells = culled
                self.highlight_color = CULL_CLR
                self.highlight_timer = FPS * 2

        elif decision == "SPORULATION":
            self.board.seed_random(SPORULATION_CELLS)
            self.highlight_color = BIRTH_CLR
            self.highlight_timer = FPS * 2

    # ── Rendering ─────────────────────────────────────────────────
    def _render(self):
        self.screen.fill(BG)
        self._draw_cells()
        self._draw_hud()
        self._draw_buttons()
        pygame.display.flip()

    def _draw_cells(self):
        highlight_set = set(self.highlight_cells) if self.highlight_timer > 0 else set()
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if self.board.is_alive(row, col):
                    color = self.highlight_color if (row, col) in highlight_set else CELL_CLR
                    rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(self.screen, color, rect)

    def _draw_hud(self):
        alive = int(self.board.grid.sum())
        density = alive / self.board.grid.size * 100

        lines = [
            f"Epoch: {self.epoch}",
            f"Alive: {alive}  Density: {density:.1f}%",
        ]

        if self.ai_decision:
            lines.append(f"AI: {self.ai_decision}")
            if self.ai_reasoning:
                lines.append(f"  {self.ai_reasoning[:60]}")

        if self.ai_running:
            lines.append("  [Quorum sensing in progress...]")

        y = 8
        for line in lines:
            surface = self.font.render(line, True, HUD_TEXT)
            bg_rect = pygame.Rect(6, y - 2, surface.get_width() + 8, surface.get_height() + 4)
            bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            bg_surface.fill(HUD_BG)
            self.screen.blit(bg_surface, bg_rect)
            self.screen.blit(surface, (10, y))
            y += 20

        if self.ai_flash_timer > 0 and self.ai_decision:
            flash_surface = self.big_font.render(
                f"QUORUM: {self.ai_decision}", True, self.highlight_color
            )
            x = WINDOW_W // 2 - flash_surface.get_width() // 2
            self.screen.blit(flash_surface, (x, GRID_H - 40))

    def _draw_buttons(self):
        pygame.draw.rect(self.screen, BAR_BG, (0, GRID_H, WINDOW_W, BAR_H))

        mouse_pos = pygame.mouse.get_pos()

        for btn, label in [
            (self.btn_pause, "▶ PLAY" if self.paused else "⏸ PAUSE"),
            (self.btn_langfuse, "🔍 LANGFUSE"),
        ]:
            hover = btn.collidepoint(mouse_pos)
            color = BTN_HOVER if hover else BTN_BG
            pygame.draw.rect(self.screen, color, btn, border_radius=4)
            text = self.btn_font.render(label, True, BTN_TEXT)
            tx = btn.x + (btn.width - text.get_width()) // 2
            ty = btn.y + (btn.height - text.get_height()) // 2
            self.screen.blit(text, (tx, ty))


def main():
    engine = Engine()
    engine.run()


if __name__ == "__main__":
    main()
