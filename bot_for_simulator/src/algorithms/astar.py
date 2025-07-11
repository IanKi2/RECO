import heapq


class AStarBot:
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.internal_state = {}
        self.vision_radius = self.config.get("vision_radius", 5)

    def step(self, state: dict) -> tuple:
        try:
            self.world_width = state.get('width')
            self.world_height = state.get('height')
            
            self._update_internal_state(state)

            route = self._make_decision()

            decision = self._get_first_direction(route)

            command_body = self._format_command(decision)
            viz_data = {"path": route}
            
            return command_body, 
    
            
        except Exception as e:
            print(f"Algorithm error: {str(e)}")
            return {"command": "attack"}, None


    def _update_internal_state(self, state: dict):
        self.internal_state["agent_pos"] = (state["agent"]["x"], state["agent"]["y"])
        self.internal_state["resources"] = state.get("resources", [])
        self.internal_state["obstacles"] = state.get("obstacles", []) + state.get("npcs", [])


    def _make_decision(self) -> list:
        # Шаг 1: Подготовка данных
        agent_pos = self.internal_state["agent_pos"]
        resources = self.internal_state.get("resources", [])
        obstacles = self.internal_state.get("obstacles", set())
        
        # Шаг 2: Проверка наличия ресурсов
        if not resources:
            return []  # Если ресурсов нет - возвращаем пустой путь

        # Шаг 3: Определение эвристической функции (манхэттенское расстояние)
        def heuristic(pos):
            min_distance = float('inf')
            for res in resources:
                # Вычисляем расстояние до каждого ресурса
                distance = abs(pos[0] - res[0]) + abs(pos[1] - res[1])
                if distance < min_distance:
                    min_distance = distance
            return min_distance

        # Шаг 4: Инициализация структур данных для A*
        open_set = []  # Приоритетная очередь (min-heap)
        heapq.heappush(open_set, (0 + heuristic(agent_pos), agent_pos))
        
        g_score = {agent_pos: 0}  # Стоимость пути от старта
        came_from = {}  # Для восстановления пути
        came_from[agent_pos] = None

        # Возможные направления движения
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        # Шаг 5: Основной цикл A*
        while open_set:
            # Извлекаем узел с наименьшей общей стоимостью (f = g + h)
            current_f, current = heapq.heappop(open_set)
            
            # Проверка на актуальность узла
            if current != agent_pos:  # Пропускаем проверку для стартовой точки
                # Если текущая стоимость g выше сохраненной - узел устарел
                if current_f - heuristic(current) > g_score[current]:
                    continue
            
            # Шаг 6: Проверка достижения цели
            if current in resources:
                # Восстановление пути
                path = []
                while current:
                    path.append(current)
                    current = came_from[current]
                return path[::-1]  # Разворачиваем путь от цели к агенту
            
            # Шаг 7: Обработка соседей
            for dx, dy in directions:
                neighbor = (current[0] + dx, current[1] + dy)
                
                # Проверка границ мира
                if (neighbor[0] < 0 or neighbor[0] >= self.world_width or
                    neighbor[1] < 0 or neighbor[1] >= self.world_height):
                    continue
                
                # Проверка на препятствия
                if neighbor in obstacles:
                    continue
                
                # Вычисление новой стоимости пути
                tentative_g = g_score[current] + 1
                
                # Если новый путь лучше существующего
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor)
                    heapq.heappush(open_set, (f_score, neighbor))
                    came_from[neighbor] = current
        
        # Шаг 8: Если путь не найден
        return []
    
    def _get_first_direction(self, path):
        """
        Определяет первое направление движения из маршрута
        :param path: Список координат в формате [(x1, y1), (x2, y2), ...]
        :return: Строка направления ('up', 'down', 'left', 'right') или None
        """
        # Проверяем, что в пути есть хотя бы 2 точки
        if len(path) < 2:
            return None
        
        # Берем стартовую позицию и следующую точку
        start_x, start_y = path[0]
        next_x, next_y = path[1]
        
        # Вычисляем разницу координат
        dx = next_x - start_x
        dy = next_y - start_y
        
        # Определяем направление по изменениям
        if dx == 1:
            return "right"
        elif dx == -1:
            return "left"
        elif dy == 1:
            return "down"
        elif dy == -1:
            return "up"
    
        # Если координаты не изменились или изменение нестандартное
        return None

    def _format_command(self, decision: str | None) -> dict:
        if decision is None:
            return {"command": "attack"}
        return {
            "command": "move",
            "direction": decision
        }