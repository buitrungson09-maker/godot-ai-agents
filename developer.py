from pathlib import Path
def develop(plan: list[str]) -> list[dict[str, str]]:
    """Produce a transparent, simulated development log."""
    if not plan:
        raise ValueError("Ke hoach khong duoc rong")
    return [{"step": step, "status": "simulated"} for step in plan]



def generate_player(output_dir="generated"):
    """Tao file player.py cho game 2D."""

    folder = Path(output_dir)
    folder.mkdir(parents=True, exist_ok=True)

    player_code = '''class Player:
    def __init__(self, x=0, y=0, speed=5):
        self.x = x
        self.y = y
        self.speed = speed

    def move(self, direction):
        if direction == "up":
            self.y -= self.speed
        elif direction == "down":
            self.y += self.speed
        elif direction == "left":
            self.x -= self.speed
        elif direction == "right":
            self.x += self.speed

    def get_position(self):
        return self.x, self.y
'''

    file_path = folder / "player.py"
    file_path.write_text(player_code, encoding="utf-8")

    return file_path