import numpy as np
from perlin_noise import PerlinNoise
import random

class Obstacle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.kind = "obstacle"
        self.is_passable = False

class Npc:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.kind = "npc"
        self.is_passable = False

class Resource:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.kind = "resource"
        self.is_passable = True

class Agent:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = 'up'
        self.kind = "agent"
        self.is_passable = False

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.entity = None
        self.resource = None

    def add_entity(self, entity):
        self.entity = entity

    def remove_entity(self):
        self.entity = None

    def add_resource(self, resource):
        self.resource = resource

    def remove_resource(self):
        self.resource = None

    def is_passable(self):
        return self.entity is None or self.entity.is_passable

    def get_state(self):
        state = {"x": self.x, "y": self.y}
        if self.entity:
            state["entity"] = self.entity.kind
        if self.resource:
            state["resource"] = True
        return state

class GameWorld:
    def __init__(self, config):
        self.config = config
        self.field_size = config['field_size']
        self.seed = config['seed']
        self.npc_count = config['npc_count']
        self.resource_count = config['resource_count']
        self.obstacle_percent = config['obstacle_percent']
        self.npc_movement = config['npc_movement']
        self.agent_vision_radius = config['agent_vision_radius']
        self.octaves = 2
        self.noise_scale = 0.15
        self.score = 0
        self.respawns = 0
        self.npcs = []
        self.resources = []
        self.obstacles = []
        self.agent = None
        self.initialize_world()

    def get_init_params(self):
        return {
            "field_size": self.field_size,
            "seed": self.seed,
            "npc_count": self.npc_count,
            "resource_count": self.resource_count,
            "obstacle_percent": self.obstacle_percent,
            "npc_movement": self.npc_movement,
            "agent_vision_radius": self.agent_vision_radius
        }

    def generate_obstacle_map(self):
        noise = PerlinNoise(octaves=self.octaves, seed=self.seed)
        noise_map = np.zeros((self.field_size, self.field_size))

        for i in range(self.field_size):
            for j in range(self.field_size):
                noise_map[i][j] = noise([i * self.noise_scale, j * self.noise_scale])

        noise_min = np.min(noise_map)
        noise_max = np.max(noise_map)
        normalized_map = (noise_map - noise_min) / (noise_max - noise_min)
        
        threshold = np.percentile(normalized_map, 100 - self.obstacle_percent)
        return (normalized_map > threshold).astype(int)

    def initialize_world(self):
        obstacle_matrix = self.generate_obstacle_map()
        self.cells = [[Cell(i, j) for j in range(self.field_size)] for i in range(self.field_size)]
        
        # Список всех возможных позиций
        all_positions = [(i, j) for i in range(self.field_size) for j in range(self.field_size)]
        random.shuffle(all_positions)
        
        # 1. Добавляем препятствия
        obstacle_positions = []
        for i, j in all_positions[:]:
            if obstacle_matrix[i][j] == 1:
                obstacle = Obstacle(i, j)
                self.cells[i][j].add_entity(obstacle)
                self.obstacles.append(obstacle)
                obstacle_positions.append((i, j))
        all_positions = [pos for pos in all_positions if pos not in obstacle_positions]
        
        # 2. Добавляем NPC
        npc_positions = random.sample(all_positions, min(self.npc_count, len(all_positions)))
        for i, j in npc_positions:
            npc = Npc(i, j)
            self.cells[i][j].add_entity(npc)
            self.npcs.append(npc)
        all_positions = [pos for pos in all_positions if pos not in npc_positions]
        
        # 3. Добавляем ресурсы
        resource_positions = random.sample(all_positions, min(self.resource_count, len(all_positions)))
        for i, j in resource_positions:
            resource = Resource(i, j)
            self.cells[i][j].add_resource(resource)
            self.resources.append(resource)
        all_positions = [pos for pos in all_positions if pos not in resource_positions]
        
        # 4. Добавляем агента
        if all_positions:
            i, j = random.choice(all_positions)
            self.agent = Agent(i, j)
            self.cells[i][j].add_entity(self.agent)

    def get_full_state(self):
        state = {
            "width": self.field_size,
            "height": self.field_size,
            "score": self.score,
            "respawns": self.respawns,
            "agent": {
                "x": self.agent.x, 
                "y": self.agent.y,
                "direction": self.agent.direction
            },
            "npcs": [{"x": npc.x, "y": npc.y} for npc in self.npcs],
            "resources": [{"x": res.x, "y": res.y} for res in self.resources],
            "obstacles": [{"x": obs.x, "y": obs.y} for obs in self.obstacles]
        }
        return state

    def handle_collision(self):
        self.score -= 10
        self.respawns += 1
        self.respawn_agent()

    def respawn_agent(self):
        free_cells = []
        for x in range(self.field_size):
            for y in range(self.field_size):
                if self.cells[x][y].is_passable():
                    free_cells.append((x, y))
        
        if free_cells:
            x, y = random.choice(free_cells)
            # Удаляем агента со старой позиции
            old_cell = self.cells[self.agent.x][self.agent.y]
            old_cell.remove_entity()
            # Размещаем на новой
            new_cell = self.cells[x][y]
            new_cell.add_entity(self.agent)
            self.agent.x, self.agent.y = x, y



