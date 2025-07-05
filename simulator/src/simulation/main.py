from flask import Flask, request, jsonify
from game_objects import GameWorld
from game_logic import process_game_tick
from validation import validate_init_params, validate_command
import threading

app = Flask(__name__)

gameworld = None
lock = threading.Lock()


@app.route('/init', methods=['POST'])
def init_game():
    global gameworld
    
    if gameworld is not None:
        return jsonify({'error': 'conflict', 'details': 'Game already initialized'}), 409
    
    config = request.get_json()
    if not config:
        return jsonify({'error': 'invalid_params', 'details': 'No configuration provided'}), 400
    
    errors, validated_config = validate_init_params(config)
    if errors:
        return jsonify({'error': 'invalid_params', 'details': errors}), 400
    
    try:
        with lock:
            gameworld = GameWorld(validated_config)
    except RuntimeError as e:
        return jsonify({'error': 'initialization_failed', 'details': str(e)}), 500
    
    response = {
        'status': 'game_initialized',
        'parameters': gameworld.get_init_params()
    }
    return jsonify(response), 200


@app.route('/status', methods=['GET'])
def status_check():
    if gameworld is None:
        return jsonify({'status': 'not initialized'}), 200
    
    try:
        parameters = gameworld.get_init_params()
        return jsonify({
            'status': 'launched',
            'parameters': parameters
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'launched',
            'error': f'Error retrieving parameters: {str(e)}'
        }), 200


@app.route('/full-state', methods=['GET'])
def get_full_state():
    if gameworld is None:
        return jsonify({
            'error': 'game_not_found',
            'message': 'Game state not initialized'
        }), 404
    
    try:
        response = gameworld.get_full_state()
        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': 'state_retrieval_failed'}), 500
    

@app.route('/command', methods=['POST'])
def handle_command():
    global gameworld
    
    if gameworld is None:
        return jsonify({
            "error": "game_not_initialized",
            "solution": "Call POST /init first"
        }), 404

    data = request.get_json()
    errors = validate_command(data)
    
    if errors:
        return jsonify({
            "error": "invalid_command",
            "details": errors
        }), 400
    
    try:
        response = process_game_tick(gameworld, data)
        return jsonify(response)
    except Exception as e:
        return jsonify({
            "error": "processing_failed",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)