import subprocess
import sys
from pathlib import Path

from cli import cli
from db import init_db


def main() -> None:
    init_db()

    bot_path = Path(__file__).resolve().with_name("telegram.py")
    bot_process = subprocess.Popen([sys.executable, str(bot_path)])

    try:
        cli()
    except KeyboardInterrupt:
        print("\nЗавершаем приложение...")
    finally:
        if bot_process.poll() is None:
            bot_process.terminate()

        try:
            bot_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            bot_process.kill()
            bot_process.wait()


if __name__ == "__main__":
    main()
