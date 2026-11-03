extends Node2D

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
