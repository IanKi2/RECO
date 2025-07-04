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

class Resours:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.kind = "resours"
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
    def __init__(self):
        # self.field_size = config['field_size']
        # self.tick_interval = config['tick_interval']
        # self.seed = config['seed']
        # self.npc_count = config['npc_count']
        # self.resource_count = config['resource_count']
        # self.obstacle_percent = config['obstacle_percent']
        # self.npc_movement = config['npc_movement']
        # self.agent_vision_radius = config['agent_vision_radius']
        # self.octaves = 2
        # self.noise_scale = 0.15
        # self.cells = []

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
        self.cells = []

        for i in range(self.field_size):
            row = []
            for j in range(self.field_size):
                cell = Cell(i, j)
                if obstacle_matrix[i][j] == 1:
                    obstacle = Obstacle(i, j)
                    cell.add_entity(obstacle)
                row.append(cell)
            self.cells.append(row)

        # Собираем все свободные клетки
        free_cells = []
        for row in self.cells:
            for cell in row:
                if cell.entity is None:
                    free_cells.append(cell)
        random.shuffle(free_cells)

        # Добавляем NPC
        for _ in range(min(self.npc_count, len(free_cells))):
            cell = free_cells.pop()
            cell.add_entity(Npc(cell.x, cell.y))

        # Добавляем ресурсы
        for _ in range(min(self.resource_count, len(free_cells))):
            cell = free_cells.pop()
            cell.add_entity(Resours(cell.x, cell.y))

        cell = free_cells.pop()
        cell.add_entity(Agent(cell.x, cell.y))

    def is_passable_at(self, x, y):
        """Проверяет, можно ли пройти через клетку по координатам"""
        if not (0 <= x < self.field_size and 0 <= y < self.field_size):
            return False  # Координаты вне мира - непроходимы

        return self.cells[x][y].is_passable()


    def is_passable_at(self, x, y):
        """Проверяет, можно ли пройти через клетку по координатам"""
        if not (0 <= x < self.field_size and 0 <= y < self.field_size):
            return False  # Координаты вне мира - непроходимы

        return self.cells[x][y].is_passable()

    def remove_entity_at(self, x, y):
        """Удаляет сущность по координатам"""
        if not (0 <= x < self.field_size and 0 <= y < self.field_size):
            return False  # Координаты вне мира

        if self.cells[x][y].entity:
            self.cells[x][y].remove_entity()
            return True
        return False

    def get_world_properties(self):
        """Возвращает свойства мира для отправки клиенту"""
        properties = {
            "width": self.field_size,
            "height": self.field_size,
            "score": "(count)",
            "respawns": "(count)",
            "agent": [],
            "npcs": [],
            "resourses": [],
            "obstacles": []
        }

        for x in range(self.field_size):
            for y in range(self.field_size):
                if (
                    self.cells[x][y].entity
                    and self.cells[x][y].entity.kind == "obstacle"
                ):
                    properties["obstacles"].append({"x": x, "y": y})

        for x in range(self.field_size):
            for y in range(self.field_size):
                if (
                    self.cells[x][y].entity
                    and self.cells[x][y].entity.kind == "npc"
                ):
                    properties["npcs"].append({"x": x, "y": y})

        for x in range(self.field_size):
            for y in range(self.field_size):
                if (
                    self.cells[x][y].entity
                    and self.cells[x][y].entity.kind == "resours"
                ):
                    properties["resourses"].append({"x": x, "y": y})

        for x in range(self.field_size):
            for y in range(self.field_size):
                if (
                    self.cells[x][y].entity
                    and self.cells[x][y].entity.kind == "agent"
                ):
                    properties["agent"].append({"x": x, "y": y})

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

    print(world.get_world_properties())


