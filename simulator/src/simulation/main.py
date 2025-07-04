from flask import Flask, request, jsonify
from game_logic import GameWorld
from validation import validate_init_params
import threading

app = Flask(__name__)

gameworld = None
lock = threading.Lock()

@app.route('/init', methods=['POST'])
def init_game():
    global gameworld
    
    # Проверка, что игра еще не инициализирована
    if gameworld is not None:
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
            gameworld = GameWorld(validated_config)
    except RuntimeError as e:
        return jsonify({'error': 'Initialization failed', 'details': str(e)}), 500
    
    # Формирование ответа
    response = gameworld.get_init_response()
    return jsonify(response), 200


@app.route('/status', methods=['GET'])
def status_check():
    
    """Проверка состояния сервера и игры"""
    response = {
        'status': 'ok',
        'service': 'game-server',
        'game_initialized': False  # По умолчанию игра не инициализирована
    }
    
    if gameworld is not None:
        try:
            # Получаем данные инициализации
            parameters = gameworld.get_init_response()
            response.update({
                'parameters': parameters
            })
        except Exception as e:
            # Ошибка при получении состояния, но игра считается инициализированной
            response.update({
                'game_initialized': True,
                'error': f'Error getting state: {str(e)}'
            })
    
    return jsonify(response), 200

@app.route('/full-state', methods=['GET'])
def get_full_state():
    """Получения полных данных игры"""
    if gameworld is None:
        return jsonify({'error': 'Initialization failed'}), 404
    
    else:
        try:
            # Получаем данные инициализации
            
            response = gameworld.get_world_properties()
            
        except Exception as e:
            # Ошибка при получении состояния, но игра считается инициализированной
            response = ({
                'game_initialized': True,
                'error': f'Error getting state: {str(e)}'
            })
    
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)