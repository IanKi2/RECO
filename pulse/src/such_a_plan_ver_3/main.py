import time
from api_handler import get_arena, post_move
from brain import Brain

def main():
    while True:
        try:
            # Получаем текущее состояние арены
            arena_data = get_arena()
            
            # Планируем ходы
            brain = Brain(arena_data)
            moves = brain.plan_moves()
            
            # Отправляем ходы на сервер
            response = post_move(moves)
            print(f"Turn {arena_data['turnNo']} completed. Score: {arena_data['score']}")
            
            # Ждем до следующего хода
            sleep_time = arena_data['nextTurnIn'] / 1000.0
            time.sleep(max(0.1, sleep_time))
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)  # Пауза перед повторной попыткой

if __name__ == "__main__":
    main()