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
    
def generate_sword_slash(output_dir="generated"):
    """Tao script ky nang kiem cho Godot 4."""

    folder = Path(output_dir) / "skills"
    folder.mkdir(parents=True, exist_ok=True)

    godot_code = '''extends Node2D

signal skill_activated(damage: int)

@export var damage: int = 20
@export var cooldown: float = 3.0

var remaining_cooldown: float = 0.0


func _process(delta: float) -> void:
    if remaining_cooldown > 0.0:
        remaining_cooldown = maxf(
            0.0, remaining_cooldown - delta
        )


func use_skill() -> bool:
    if remaining_cooldown > 0.0:
        return false

    remaining_cooldown = cooldown
    skill_activated.emit(damage)
    return true
'''

    file_path = folder / "sword_slash.gd"
    file_path.write_text(godot_code, encoding="utf-8")

    return file_path
