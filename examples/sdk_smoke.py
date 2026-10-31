"""Demo rieng de kiem tra OpenAI Agents SDK; khong sua file game.

Chay sau khi cai requirements-agents.txt va dat OPENAI_API_KEY.
Demo nay goi API (co the phat sinh chi phi); khong nam trong offline pipeline.
"""

import os


def main() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit(
            "Chua co OPENAI_API_KEY. Dat bien moi truong truoc khi chay demo."
        )

    from agents import Agent, Runner

    planner = Agent(
        name="Godot Planner - demo",
        instructions=(
            "Ban la Planner ho tro lam game tu tien 2D bang Godot 4. "
            "Hay lap ke hoach ngan gon bang tieng Viet. "
            "Chi dua ra goi y, khong khang dinh da sua game."
        ),
    )
    task = "Lap ke hoach tao ky nang chem kiem co cooldown 3 giay."
    result = Runner.run_sync(planner, task)
    print(result.final_output)


if __name__ == "__main__":
    main()
