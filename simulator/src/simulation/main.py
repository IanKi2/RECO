from flask import Flask, request, jsonify
from game_logic import GameWorld
from validation import validate_init_params
import threading

app = Flask(__name__)

# Глобальное состояние игры
game_state = None
lock = threading.Lock()

@app.route('/init', methods=['POST'])
def init_game():
    global game_state
    
    # Проверка, что игра еще не инициализирована
    if game_state is not None:
        return jsonify({'error': 'Game already initialized'}), 409
    
    # Получение и валидация параметров
    config = request.get_json()
    if not config:
        return jsonify({'error': 'No configuration provided'}), 400
    
    errors, validated_config = validate_init_params(config)
    if errors:
        return jsonify({'error': 'Invalid parameters', 'details': errors}), 400
    
    # Создание состояния игры
    try:
        with lock:
            game_state = GameWorld(validated_config)
    except RuntimeError as e:
        return jsonify({'error': 'Initialization failed', 'details': str(e)}), 500
    
    # Формирование ответа
    response = game_state.get_init_response()
    return jsonify(response), 200


@app.route('/status', methods=['GET'])
def status_check():
    """Проверка состояния сервера и игры"""
    response = {
        'status': 'ok',
        'service': 'game-server',
        'game_initialized': False  # По умолчанию игра не инициализирована
    }
    
    if game_state is not None:
        try:
            # Получаем данные инициализации
            parameters = game_state.get_init_response()
            response.update({
                'parameters': parameters
            })
        except Exception as e:
            # Ошибка при получении состояния, но игра считается инициализированной
            response.update({
                'game_initialized': True,
                'error': f'Ошибка получения состояния: {str(e)}'
            })
    
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)