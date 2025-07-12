# main.py
from api_handler import get_arena, post_move
from brain import decide_moves
import time

def main():
    while True:
        try:
            data = get_arena()
            moves = decide_moves(data)
            response = post_move(moves)
            print(f"Turn {data['turnNo']} completed. Next in {data['nextTurnIn']}ms")
            
            # Ожидание следующего хода
            sleep_time = max(0, data['nextTurnIn'] / 1000.0 - 0.05)  # Запас 50 мс
            time.sleep(sleep_time)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()