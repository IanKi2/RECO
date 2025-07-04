import random

def validate_init_params(config):
    """Валидация параметров инициализации игры"""
    errors = []
    
    # Проверка обязательных параметров
    required_params = [
        'field_size', 'tick_interval', 'npc_count', 'resource_count',
        'obstacle_percent', 'npc_movement', 'agent_vision_radius'
    ]
    missing = [p for p in required_params if p not in config]
    if missing:
        errors.append(f'Missing parameters: {", ".join(missing)}')
        return errors, None
    
    # Извлечение параметров
    field_size = config['field_size']
    tick_interval = config['tick_interval']
    npc_count = config['npc_count']
    resource_count = config['resource_count']
    obstacle_percent = config['obstacle_percent']
    vision_radius = config['agent_vision_radius']
    
    # Проверка диапазонов значений
    if not 10 <= field_size <= 1000:
        errors.append('field_size must be between 10 and 1000')
    
    if not 1 <= tick_interval <= 5:
        errors.append('tick_interval must be between 1 and 5 seconds')
    
    if not 0 <= npc_count <= 1000:
        errors.append('npc_count must be between 0 and 1000')
    
    if not 0 <= resource_count <= 1000:
        errors.append('resource_count must be between 0 and 1000')
    
    if not 0 <= obstacle_percent <= 30:
        errors.append('obstacle_percent must be between 0 and 30')

    if not 5 <= vision_radius <= 1000:
        errors.append('vision_radius must be between 10 and 1000')

    
    # Проверка доступности места на поле
    total_cells = field_size ** 2

    if npc_count > int(total_cells * 0.10):
        errors.append('too much npc')

    if resource_count > int(total_cells * 0.10):
        errors.append('too much resource')

    obstacle_cells = int(total_cells * obstacle_percent / 100)

    required_cells = 1 + obstacle_cells - npc_count - resource_count - 1
    
    if required_cells > total_cells:
        errors.append(f'Not enough free space: requires {required_cells} cells, total_cells {total_cells}')

    # Добавление seed, если не указан
    config['seed'] = config.get('seed', random.randint(1, 1000000))
    
    return errors, config