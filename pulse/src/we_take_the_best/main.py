import time
from api_handler import get_arena, post_move
from brain import Bot

bot = Bot()
MIN_SLEEP = 0.1  # Минимальное время между запросами

def main():
    while True:
        try:
            start_time = time.time()
            state = get_arena()
            
            # Обработка состояния
            moves = bot.process_turn(state)
            response = post_move(moves)
            
            # Ожидание следующего хода
            next_turn = state.get('nextTurnIn', 1000) / 1000
            elapsed = time.time() - start_time
            sleep_time = max(next_turn - elapsed, MIN_SLEEP)
            time.sleep(sleep_time)
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(MIN_SLEEP)

if __name__ == "__main__":
    main()