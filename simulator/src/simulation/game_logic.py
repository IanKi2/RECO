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
        self.kind = "agent"
        self.is_passable = False

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.entity = None  # Сущность на клетке

    def add_entity(self, entity):
        """Добавляет сущность на клетку"""
        self.entity = entity

    def remove_entity(self):
        """Удаляет сущность с клетки"""
        self.entity = None

    def is_passable(self):
        """Проверяет, можно ли пройти через клетку"""
        return self.entity is None or self.entity.is_passable

    def get_cell_properties(self):
        """Исправленный метод с проверкой на наличие сущности"""
        if self.entity:
            return {
                "x": self.x,
                "y": self.y,
                "kind": self.entity.kind,
                "is_passable": self.entity.is_passable,
            }
        else:
            return {"x": self.x, "y": self.y, "kind": "empty", "is_passable": True}


class GameWorld:
    def __init__(self, config):
        self.field_size = config['field_size']
        self.tick_interval = config['tick_interval']
        self.seed = config['seed']
        self.npc_count = config['npc_count']
        self.resource_count = config['resource_count']
        self.obstacle_percent = config['obstacle_percent']
        self.npc_movement = config['npc_movement']
        self.agent_vision_radius = config['agent_vision_radius']
        self.octaves = 2
        self.noise_scale = 0.15
        self.initialize_world()



    def generate_obstacle_map(self):
        """Генерация карты препятствий с использованием шума Перлина"""
        noise = PerlinNoise(octaves=self.octaves, seed=self.seed)
        noise_map = np.zeros((self.field_size, self.field_size))

        for i in range(self.field_size):
            for j in range(self.field_size):
                noise_map[i][j] = noise([i * self.noise_scale, j * self.noise_scale])

        # Нормализация значений
        noise_min = np.min(noise_map)
        noise_max = np.max(noise_map)
        normalized_map = (noise_map - noise_min) / (noise_max - noise_min)

        # Определение порога для нужного процента препятствий
        threshold = np.percentile(normalized_map, 100 - self.obstacle_percent)
        return (normalized_map > threshold).astype(int)

    def initialize_world(self):
        obstacle_matrix = self.generate_obstacle_map()
        self.cells = [[Cell(i, j) for j in range(self.field_size)] for i in range(self.field_size)]
        
        # Список всех возможных позиций
        all_positions = [(i, j) for i in range(self.field_size) for j in range(self.field_size)]
        random.shuffle(all_positions)
        
        # 1. Добавляем препятствия (с правильной индексацией)
        obstacle_positions = []
        for i, j in all_positions[:]:  # Используем копию списка
            if obstacle_matrix[i][j] == 1:  # Правильная индексация [i][j]
                self.cells[i][j].add_entity(Obstacle(i, j))
                obstacle_positions.append((i, j))
        
        # Удаляем позиции с препятствиями из общего списка
        all_positions = [pos for pos in all_positions if pos not in obstacle_positions]
        
        # 2. Добавляем NPC
        npc_positions = random.sample(all_positions, min(self.npc_count, len(all_positions)))
        for i, j in npc_positions:
            self.cells[i][j].add_entity(Npc(i, j))
        
        # Удаляем позиции NPC
        all_positions = [pos for pos in all_positions if pos not in npc_positions]
        
        # 3. Добавляем ресурсы
        resource_positions = random.sample(all_positions, min(self.resource_count, len(all_positions)))
        for i, j in resource_positions:
            self.cells[i][j].add_entity(Resource(i, j))  # Используем правильный класс
        
        # Удаляем позиции ресурсов
        all_positions = [pos for pos in all_positions if pos not in resource_positions]
        
        # 4. Добавляем агента
        if all_positions:
            i, j = random.choice(all_positions)
            self.cells[i][j].add_entity(Agent(i, j))

    # def is_passable_at(self, x, y):
    #     """Проверяет, можно ли пройти через клетку по координатам"""
    #     if not (0 <= x < self.field_size and 0 <= y < self.field_size):
    #         return False  # Координаты вне мира - непроходимы

    #     return self.cells[x][y].is_passable()


    # def is_passable_at(self, x, y):
    #     """Проверяет, можно ли пройти через клетку по координатам"""
    #     if not (0 <= x < self.field_size and 0 <= y < self.field_size):
    #         return False  # Координаты вне мира - непроходимы

    #     return self.cells[x][y].is_passable()

    # def remove_entity_at(self, x, y):
    #     """Удаляет сущность по координатам"""
    #     if not (0 <= x < self.field_size and 0 <= y < self.field_size):
    #         return False  # Координаты вне мира

    #     if self.cells[x][y].entity:
    #         self.cells[x][y].remove_entity()
    #         return True
    #     return False


    def get_world_properties(self):
        """Исправленный метод с правильными ключами JSON"""
        properties = {
            "width": self.field_size,
            "height": self.field_size,
            "score": "(count)",
            "respawns": "(count)",
            "agent": [],
            "npcs": [],
            "resources": [],  # Ключ "resourses" (во множественном числе)
            "obstacles": []
        }

        for i in range(self.field_size):
            for j in range(self.field_size):
                cell = self.cells[i][j]
                if cell.entity:
                    entity_info = {"x": i, "y": j}  # Используем координаты клетки
                    kind = cell.entity.kind
                    
                    if kind == "obstacle":
                        properties["obstacles"].append(entity_info)
                    elif kind == "npc":
                        properties["npcs"].append(entity_info)
                    elif kind == "resource":  # Сущность имеет kind="resource"
                        properties["resources"].append(entity_info)  # Но ключ "resourses"
                    elif kind == "agent":
                        properties["agent"].append(entity_info)
        
        return properties

    def get_init_response(self):
        """Данные для ответа после инициализации"""
        return {
            "status": "initialized",
            "field_size": self.field_size,
            "tick_interval": self.tick_interval,
            "seed": self.seed,
            "npc_count": self.npc_count,
            "resource_count": self.resource_count,
            "obstacle_percent": self.obstacle_percent,
            "npc_movement": self.npc_movement,
            "agent_vision_radius": self.agent_vision_radius,
        }



