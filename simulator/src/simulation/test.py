import numpy as np
from perlin_noise import PerlinNoise
import random

class Obstacle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_passable = False  # Препятствия непроходимы
        self.kind = "obstacle"

    def __str__(self):
        return "🟧"  # Символ для препятствия


class Npc:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.kind = "npc"
        self.is_passable = False

    def __str__(self):
        return "🔴"  # Символ для препятствия


class Resource:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.kind = "resource"
        self.is_passable = True

    def __str__(self):
        return "🟡"  # Символ для препятствия


class Agent:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.kind = "agent"
        self.is_passable = False

    def __str__(self):
        return "⏹️"  # Символ для препятствия


class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.entity = None  # Сущность на клетке

    def __str__(self):
        return str(self.entity) if self.entity else "⬛"

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
    def __init__(self):

        self.field_size = 5
        self.seed = 42
        self.npc_count = 3
        self.resource_count = 3
        self.obstacle_percent = 30
        self.octaves = 2
        self.noise_scale = 0.15
        self.cells = []  # 2D-массив клеток
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

    

    def visualize(self, size=100):
        """Визуализирует часть карты"""
        print("\nКарта игрового мира:")
        for i in range(min(size, self.field_size)):
            for j in range(min(size, self.field_size)):
                print(self.cells[i][j], end=" ")
            print()


    def get_world_properties(self):
        """Исправленный метод с правильными ключами JSON"""
        properties = {
            "width": self.field_size,
            "height": self.field_size,
            "score": "(count)",
            "respawns": "(count)",
            "agent": [],
            "npcs": [],
            "resourses": [],  # Ключ "resourses" (во множественном числе)
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
                        properties["resourses"].append(entity_info)  # Но ключ "resourses"
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
    

    # Пример использования
if __name__ == "__main__":
    # Создаем мир
    world = GameWorld()

    world.visualize()

    print(world.get_world_properties())





