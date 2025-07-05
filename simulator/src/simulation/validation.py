import random

def validate_init_params(config):
    errors = []

    required_params = [
        'field_size', 'npc_count', 'resource_count',
        'obstacle_percent', 'npc_movement', 'agent_vision_radius'
    ]

    missing = [p for p in required_params if p not in config]
    if missing:
        errors.append(f'Missing required parameters: {", ".join(missing)}')
        return errors, None
    
    field_size = config['field_size']
    npc_count = config['npc_count']
    resource_count = config['resource_count']
    obstacle_percent = config['obstacle_percent']
    vision_radius = config['agent_vision_radius']
    npc_movement = config['npc_movement']
    
    if not isinstance(npc_movement, bool):
        errors.append('npc_movement must be boolean')
    
    if not 10 <= field_size <= 1000:
        errors.append('field_size must be between 10 and 1000')
    
    if not 0 <= npc_count <= 1000:
        errors.append('npc_count must be between 0 and 1000')
    
    if not 0 <= resource_count <= 1000:
        errors.append('resource_count must be between 0 and 1000')
    
    if not 0 <= obstacle_percent <= 30:
        errors.append('obstacle_percent must be between 0 and 30')

    if not 5 <= vision_radius <= 1000:
        errors.append('agent_vision_radius must be between 5 and 1000')
    

    total_cells = field_size ** 2
    max_entities = total_cells * 0.10  # Макс 10% поля для каждого типа сущностей

    if npc_count > max_entities:
        errors.append(f'npc_count exceeds 10% of field size (max {int(max_entities)})')

    if resource_count > max_entities:
        errors.append(f'resource_count exceeds 10% of field size (max {int(max_entities)})')
    
    obstacle_count = int(total_cells * obstacle_percent / 100)
    required_cells = 1 + obstacle_count + npc_count + resource_count
    
    if required_cells > total_cells:
        errors.append(f'Not enough space: requires {required_cells} cells but only {total_cells} available')

    config['seed'] = config.get('seed', random.randint(1, 1000000))
    
    return (errors, config) if not errors else (errors, None)


def validate_command(data):
    """
    Валидирует команду игрока
    Возвращает список ошибок (пустой список если ошибок нет)
    """
    errors = []
    
    if 'command' not in data:
        errors.append('Missing required parameter: command')
        return errors
    
    command = data['command']
    
    valid_commands = ['move', 'attack']
    if command not in valid_commands:
        errors.append(f'Invalid command: {command}. Valid commands: {", ".join(valid_commands)}')
    
    if command == 'move':
        if 'direction' not in data:
            errors.append('Move command requires direction parameter')
        else:
            direction = data['direction']
            valid_directions = ['up', 'down', 'left', 'right']
            
            if direction not in valid_directions:
                errors.append(f'Invalid direction: {direction}. Valid directions: {", ".join(valid_directions)}')
    
    return errors