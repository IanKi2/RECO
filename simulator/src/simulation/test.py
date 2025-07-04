import numpy as np
from perlin_noise import PerlinNoise


class Obstacle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_passable = False  # Препятствия непроходимы
        self.kind = "obstacle"

    def __str__(self):
        return "🟧"  # Символ для препятствия


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
                "is_passable": self.entity.is_passable
            }
        else:
            return {
                "x": self.x,
                "y": self.y,
                "kind": "empty",
                "is_passable": True
            }


class GameWorld:
    def __init__(self):
        self.field_size = 5
        self.seed = 42
        self.obstacle_percent = 30
        self.octaves = 2
        self.noise_scale = 0.15
        self.cells = []  # 2D-массив клеток

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

    def create_world(self):
        """Создает игровой мир с клетками и препятствиями"""
        obstacle_matrix = self.generate_obstacle_map()
        self.cells = []

        # Создаем сетку клеток
        for i in range(self.field_size):
            row = []
            for j in range(self.field_size):
                cell = Cell(i, j)

                # Если в матрице препятствий 1 - создаем препятствие
                if obstacle_matrix[i][j] == 1:
                    obstacle = Obstacle(i, j)
                    cell.add_entity(obstacle)

                row.append(cell)
            self.cells.append(row)
        return self

    def visualize(self, size=10):
        """Визуализирует часть карты"""
        print("\nКарта игрового мира:")
        for i in range(min(size, self.field_size)):
            for j in range(min(size, self.field_size)):
                print(self.cells[i][j], end=" ")
            print()

    def is_passable_at(self, x, y):
        """Проверяет, можно ли пройти через клетку по координатам"""
        if not (0 <= x < self.field_size and 0 <= y < self.field_size):
            return False  # Координаты вне мира - непроходимы

        return self.cells[x][y].is_passable()

    def get_entity_at(self, x, y):
        """Возвращает сущность по координатам"""
        if not (0 <= x < self.field_size and 0 <= y < self.field_size):
            return None  # Координаты вне мира

        return self.cells[x][y].entity

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
            "obstacles": []  # Только препятствия
        }
        
        for x in range(self.field_size):
            for y in range(self.field_size):
                if self.cells[x][y].entity and self.cells[x][y].entity.kind == "obstacle":
                    properties["obstacles"].append({"x": x, "y": y})
        
        return properties



# Пример использования
if __name__ == "__main__":
    # Создаем мир
    world = GameWorld().create_world()

    # Визуализируем часть карты
    world.visualize(size=10)

    print(world.get_world_properties())

