import sys
import json
import threading
import traceback
import webbrowser

from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import pygame

import interventions
from board import Board
from telemetry import Telemetry
from workflow import graph


# ── Display settings ──────────────────────────────────────────────
MAX_CELL_SIZE = 20
MIN_CELL_SIZE = 4
BOARD_ROWS = 60
BOARD_COLS = 80
BAR_H = 50
SCREEN_FILL = 0.85    # leave room for the menu bar, dock and title bar
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
AI_INTERVAL = 50    # intervention sizes live in interventions.py


class Engine:
    def __init__(self):
        pygame.init()
        # Size cells to the display so the window (and its button bar) fits
        # a laptop or a 720p projector alike.
        info = pygame.display.Info()
        fit_w = int(info.current_w * SCREEN_FILL) // BOARD_COLS
        fit_h = (int(info.current_h * SCREEN_FILL) - BAR_H) // BOARD_ROWS
        self.cell_size = max(MIN_CELL_SIZE, min(MAX_CELL_SIZE, fit_w, fit_h))
        self.window_w = BOARD_COLS * self.cell_size
        self.grid_h = BOARD_ROWS * self.cell_size
        self.screen = pygame.display.set_mode((self.window_w, self.grid_h + BAR_H))
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
        # A decision is an event: logged on the one epoch it lands, then cleared.
        # ai_decision/ai_reasoning above stay set for the HUD.
        self.pending_event: tuple[str, str] | None = None
        self.ai_flash_timer = 0
        self.ai_running = False
        self.highlight_cells: list[tuple[int, int]] = []
        self.highlight_color = BIRTH_CLR
        self.highlight_timer = 0
        self.paused = False
        self.step_requested = False

        self.btn_font = pygame.font.SysFont("Consolas", 18, bold=True)
        btn_w, btn_h = 150, 36
        btn_y = self.grid_h + (BAR_H - btn_h) // 2
        self.btn_pause = pygame.Rect(10, btn_y, btn_w, btn_h)
        self.btn_step = pygame.Rect(170, btn_y, btn_w, btn_h)
        self.btn_langfuse = pygame.Rect(330, btn_y, btn_w, btn_h)

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
                if event.key in (pygame.K_RIGHT, pygame.K_n):
                    self._request_step()
                if event.key == pygame.K_r:
                    self.board = Board.from_size(BOARD_ROWS, BOARD_COLS)
                    self.board.seed_random(300)
                    self.epoch = 0
                    self.pending_event = None
                    if self.telemetry:
                        self.telemetry.clear()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.btn_pause.collidepoint(event.pos):
                    self.paused = not self.paused
                    print(f"[engine] {'Paused' if self.paused else 'Resumed'}")
                elif self.btn_step.collidepoint(event.pos):
                    self._request_step()
                elif self.btn_langfuse.collidepoint(event.pos):
                    webbrowser.open("http://localhost:3000")
                    print("[engine] Opened Langfuse dashboard")
        return True

    def _request_step(self):
        """Advance exactly one generation; pauses first so the step is visible."""
        self.paused = True
        self.step_requested = True

    def _update(self):
        if self.paused and not self.step_requested:
            return
        self.step_requested = False
        self.board.step()
        self.epoch += 1

        event, self.pending_event = self.pending_event, None
        decision, reasoning = event or ("", "")

        if self.telemetry:
            try:
                self.telemetry.record(
                    self.board.grid,
                    ai_decision=decision,
                    ai_reasoning=reasoning,
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
                self.pending_event = (self.ai_decision, self.ai_reasoning)
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
        changed = interventions.apply(decision, self.board)
        if changed:
            self.highlight_cells = changed
            self.highlight_color = CULL_CLR if decision == "PHAGE_CULL" else BIRTH_CLR
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
                    size = self.cell_size
                    rect = pygame.Rect(col * size, row * size, size, size)
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
            x = self.window_w // 2 - flash_surface.get_width() // 2
            self.screen.blit(flash_surface, (x, self.grid_h - 40))

    def _draw_buttons(self):
        pygame.draw.rect(self.screen, BAR_BG, (0, self.grid_h, self.window_w, BAR_H))

        mouse_pos = pygame.mouse.get_pos()

        for btn, label in [
            # Plain ASCII: the fallback font on macOS has no glyphs for ▶ ⏸ 🔍
            (self.btn_pause, "PLAY" if self.paused else "PAUSE"),
            (self.btn_step, "STEP >"),
            (self.btn_langfuse, "LANGFUSE"),
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
