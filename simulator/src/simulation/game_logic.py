

class GameState:
    def __init__(self, config):
        self.field_size = config['field_size']
        self.tick_interval = config['tick_interval']
        self.seed = config['seed']
        self.npc_count = config['npc_count']
        self.resource_count = config['resource_count']
        self.obstacle_percent = config['obstacle_percent']
        self.npc_movement = config['npc_movement']
        self.agent_vision_radius = config['agent_vision_radius']
        # self.initialize_world()

    # def initialize_world(self):
    #     """Инициализация игрового мира"""
    #     width = height = self.field_size
    #     total_cells = width * height
        
    #     # Установка seed для детерминированности
    #     random.seed(self.seed)
        
    #     # 1. Генерация препятствий
    #     obstacle_count = int(total_cells * self.obstacle_percent / 100)
    #     self.obstacles = set()
    #     while len(self.obstacles) < obstacle_count:
    #         x = random.randint(0, width - 1)
    #         y = random.randint(0, height - 1)
    #         self.obstacles.add((x, y))
        
    #     # 2. Размещение агента
    #     self.agent = {
    #         'x': random.randint(0, width - 1),
    #         'y': random.randint(0, height - 1),
    #         'score': 0,
    #         'respawns': 0
    #     }
        
    #     # 3. Генерация NPC (избегаем препятствий и позиции агента)
    #     self.npcs = {}
    #     for npc_id in range(1, self.npc_count + 1):
    #         placed = False
    #         attempts = 0
    #         while not placed and attempts < 100:
    #             x = random.randint(0, width - 1)
    #             y = random.randint(0, height - 1)
    #             # Проверка на свободную клетку
    #             if (x, y) not in self.obstacles and (x, y) != (self.agent['x'], self.agent['y']):
    #                 self.npcs[npc_id] = {'x': x, 'y': y}
    #                 placed = True
    #             attempts += 1
    #         if not placed:
    #             raise RuntimeError(f"Failed to place NPC {npc_id} after 100 attempts")
        
    #     # 4. Генерация ресурсов (могут быть на любых свободных клетках)
    #     self.resources = set()
    #     while len(self.resources) < self.resource_count:
    #         x = random.randint(0, width - 1)
    #         y = random.randint(0, height - 1)
    #         # Ресурсы могут быть на клетках с NPC, но не на препятствиях
    #         if (x, y) not in self.obstacles:
    #             self.resources.add((x, y))
    
    def get_init_response(self):
        """Данные для ответа после инициализации"""
        return {
            'status': 'initialized',
            'field_size': self.field_size,
            'tick_interval': self.tick_interval,
            'seed': self.seed,
            'npc_count': self.npc_count,
            'resource_count': self.resource_count,
            'obstacle_percent': self.obstacle_percent,
            'npc_movement': self.npc_movement,
            'agent_vision_radius': self.agent_vision_radius
        }