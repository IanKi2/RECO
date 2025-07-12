from utils import get_neighbors, hex_distance, direction_score
import math

RESOURCE_VALUES = {1: 10, 2: 20, 3: 60}
UNIT_MOVEMENT_POINTS = {0: 5, 1: 4, 2: 7}
DEFENSE_RADIUS = 1  # Защищаем соседние клетки

class Bot:
    def __init__(self):
        self.defense_positions = []
        self.home_hexes = []
        self.spot = None
        self.hex_info = {}
        self.enemy_hills = []
        self.reserved_cells = set()

    def update_state(self, state):
        """Обновление состояния игры"""
        self.home_hexes = [(h['q'], h['r']) for h in state['home']]
        self.spot = (state['spot']['q'], state['spot']['r'])
        self.hex_info = {}
        self.enemy_hills = []
        self.reserved_cells = set()
        
        # Сохраняем информацию о гексах
        for hex_cell in state['map']:
            pos = (hex_cell['q'], hex_cell['r'])
            self.hex_info[pos] = hex_cell
            if hex_cell['type'] == 1 and pos not in self.home_hexes:
                self.enemy_hills.append(pos)
        
        # Расчет защитных позиций
        self.defense_positions = self._calculate_defense_positions()
    
    def _calculate_defense_positions(self):
        """Вычисление всех защитных позиций вокруг муравейника"""
        defense_positions = set()
        for home_hex in self.home_hexes:
            for neighbor in get_neighbors(*home_hex):
                # Включаем только соседние гексы вне муравейника
                if neighbor not in self.home_hexes:
                    defense_positions.add(neighbor)
        return list(defense_positions)

    def process_turn(self, state):
        """Обработка хода"""
        self.update_state(state)
        moves = []
        occupied = self._get_occupied_cells(state)
        
        # Обработка бойцов в первую очередь
        fighters = [ant for ant in state['ants'] if ant['type'] == 1]
        for ant in fighters:
            ant_pos = (ant['q'], ant['r'])
            path = self._defend_home(ant_pos, UNIT_MOVEMENT_POINTS[1], occupied)
            moves.append({"ant_id": ant['id'], "path": path})
            # Резервируем финальную позицию
            self.reserved_cells.add(path[-1])
        
        # Обработка остальных юнитов
        for ant in state['ants']:
            if ant['type'] == 1:  # Бойцы уже обработаны
                continue
                
            ant_pos = (ant['q'], ant['r'])
            ant_type = ant['type']
            move_points = UNIT_MOVEMENT_POINTS[ant_type]
            
            # Логика для юнитов с ресурсами
            if ant['food']['amount'] > 0:
                path = self._return_home(ant_pos, move_points, occupied)
            
            # Логика для сбора ресурсов
            else:
                resources = self._get_visible_resources(state)
                path = self._collect_resources(ant_pos, move_points, resources, occupied)
            
            moves.append({"ant_id": ant['id'], "path": path})
            self.reserved_cells.add(path[-1])
            
        return moves

    def _get_occupied_cells(self, state):
        """Получение занятых клеток с учетом резервирования"""
        occupied = set()
        # Вражеские юниты
        for enemy in state['enemies']:
            occupied.add((enemy['q'], enemy['r']))
        # Дружественные юниты
        for ant in state['ants']:
            occupied.add((ant['q'], ant['r']))
        # Зарезервированные клетки
        occupied.update(self.reserved_cells)
        return occupied

    def _get_visible_resources(self, state):
        """Форматирование видимых ресурсов"""
        return [{
            "pos": (f['q'], f['r']),
            "type": f['type'],
            "amount": f['amount'],
            "value": RESOURCE_VALUES[f['type']] * f['amount']
        } for f in state['food']]

    def _return_home(self, start, move_points, occupied):
        """Возвращение домой с ресурсами"""
        # Выбор ближайшего гекса муравейника
        best_goal = min(
            self.home_hexes,
            key=lambda h: hex_distance(start, h)
        )
        return self._find_path(
            start, 
            best_goal, 
            move_points, 
            occupied,
            must_reach=True
        )

    def _collect_resources(self, start, move_points, resources, occupied):
        """Сбор ресурсов"""
        if not resources:
            return self._explore(start, move_points, occupied)
        
        # Выбор лучшего ресурса по ценности/расстоянию
        best_resource = None
        best_score = -math.inf
        
        for res in resources:
            dist = hex_distance(start, res['pos'])
            if dist == 0:
                efficiency = math.inf
            else:
                efficiency = res['value'] / dist
                
            if efficiency > best_score:
                best_score = efficiency
                best_resource = res
                
        return self._find_path(
            start,
            best_resource['pos'],
            move_points,
            occupied,
            must_reach=True
        )

    def _defend_home(self, start, move_points, occupied):
        """Занятие защитной позиции"""
        # Если уже на защитной позиции - остаемся
        if start in self.defense_positions:
            return [start]
        
        # Фильтрация свободных защитных позиций
        free_positions = [
            p for p in self.defense_positions 
            if p not in occupied
        ]
        
        if not free_positions:
            # Если нет свободных позиций - остаемся на месте
            return [start]
        
        # Выбор ближайшей свободной позиции
        best_pos = min(
            free_positions,
            key=lambda p: hex_distance(start, p)
        )
        
        return self._find_path(
            start,
            best_pos,
            move_points,
            occupied,
            must_reach=True
        )

    def _explore(self, start, move_points, occupied):
        """Исследование территории"""
        # Создаем путь с учетом максимального удаления
        path = [start]
        current = start
        remaining = move_points
        
        while remaining > 0:
            neighbors = get_neighbors(*current)
            valid_moves = []
            
            for pos in neighbors:
                # Проверка доступности
                if pos in occupied:
                    continue
                if pos not in self.hex_info:
                    continue
                if self.hex_info[pos]['cost'] > remaining:
                    continue
                if not self._is_safe_position(pos):
                    continue
                
                valid_moves.append(pos)
            
            if not valid_moves:
                break
                
            # Выбор направления, максимально удаляющего от базы
            best_move = max(
                valid_moves,
                key=lambda p: hex_distance(p, self.spot)
            )
            
            # Добавляем шаг в путь
            path.append(best_move)
            current = best_move
            remaining -= self.hex_info[best_move]['cost']
            
        return path

    def _is_safe_position(self, pos):
        """Проверка безопасности позиции"""
        for hill in self.enemy_hills:
            if hex_distance(pos, hill) <= 2:
                return False
        return True

    def _find_path(self, start, goal, move_points, occupied, must_reach=False):
        """Поиск пути к цели"""
        path = [start]
        current = start
        remaining = move_points
        
        while current != goal and remaining > 0:
            neighbors = get_neighbors(*current)
            best_neighbor = None
            best_score = float('inf')
            
            for pos in neighbors:
                # Проверка доступности
                if pos in occupied:
                    continue
                if pos not in self.hex_info:
                    continue
                
                # Проверка стоимости
                cost = self.hex_info[pos]['cost']
                if cost > remaining:
                    continue
                
                # Проверка безопасности
                if not self._is_safe_position(pos):
                    continue
                
                # Оценка направления
                score = direction_score(pos, goal) * 1000 + cost
                if score < best_score:
                    best_score = score
                    best_neighbor = pos
                    best_cost = cost
            
            if best_neighbor is None:
                if must_reach:
                    # Попытка найти любой доступный путь
                    for pos in neighbors:
                        if pos in occupied or pos not in self.hex_info:
                            continue
                        cost = self.hex_info[pos]['cost']
                        if cost <= remaining:
                            best_neighbor = pos
                            best_cost = cost
                            break
                if best_neighbor is None:
                    break
            
            # Добавляем шаг в путь
            path.append(best_neighbor)
            current = best_neighbor
            remaining -= best_cost
            occupied.add(current)  # Резервируем клетку
            
        return path