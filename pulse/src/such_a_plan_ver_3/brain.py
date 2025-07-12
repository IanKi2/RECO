class Brain:
    def __init__(self, arena_data):
        self.arena = arena_data
        self.spot = (arena_data['spot']['q'], arena_data['spot']['r'])
        self.home = [(h['q'], h['r']) for h in arena_data['home']]
        self.grid = {(hex_data['q'], hex_data['r']): hex_data for hex_data in arena_data['map']}
        
        # Собираем непроходимые гексы: камни и вражеские муравейники
        self.blocked_hexes = set()
        for hex_data in arena_data['map']:
            pos = (hex_data['q'], hex_data['r'])
            if hex_data['type'] == 5:  # Камни
                self.blocked_hexes.add(pos)
            elif hex_data['type'] == 1 and pos not in self.home:  # Вражеские муравейники
                self.blocked_hexes.add(pos)
        
        # Начальные позиции всех юнитов (наши + враги)
        self.occupied_start = set()
        for ant in arena_data.get('ants', []):
            self.occupied_start.add((ant['q'], ant['r']))
        for enemy in arena_data.get('enemies', []):
            self.occupied_start.add((enemy['q'], enemy['r']))

    def plan_moves(self):
        moves = []
        blocked_hexes = self.blocked_hexes | self.occupied_start
        
        # Обрабатываем юнитов в порядке ID
        ants_sorted = sorted(self.arena.get('ants', []), key=lambda x: x['id'])
        planned_paths = []
        
        for ant in ants_sorted:
            ant_id = ant['id']
            current_pos = (ant['q'], ant['r'])
            ant_type = ant['type']
            op = self._get_op(ant_type)
            
            # Правило 3: Если в кислоте - остаемся
            if self._is_acid(current_pos):
                path = [current_pos]
                planned_paths.append({"ant_id": ant_id, "path": path})
                blocked_hexes.add(current_pos)
                continue
            
            # Правило 1: Если несет ресурс - ищем кислоту
            if ant.get('food', {}).get('amount', 0) > 0:
                path = self._find_acid_path(current_pos, op, blocked_hexes)
            # Правило 2: Если видит ресурс - ищем кислоту
            elif self._sees_resource():
                path = self._find_acid_path(current_pos, op, blocked_hexes)
            # Правило 4: Ищем кислоту, удаляясь от муравейника
            else:
                path = self._explore_away_from_hill(current_pos, op, blocked_hexes)
            
            # Если путь не найден - остаемся на месте
            if not path:
                path = [current_pos]
            
            planned_paths.append({"ant_id": ant_id, "path": path})
            
            # Блокируем все гексы пути (кроме стартового)
            for pos in path[1:]:
                blocked_hexes.add(pos)
        
        # Форматируем ответ
        for plan in planned_paths:
            moves.append({
                "ant": plan["ant_id"],
                "path": [{"q": pos[0], "r": pos[1]} for pos in plan["path"]]
            })
        return moves

    def _get_op(self, ant_type):
        # ОП для типов юнитов
        return {0: 5, 1: 4, 2: 7}.get(ant_type, 0)

    def _is_acid(self, pos):
        hex_data = self.grid.get(pos)
        return hex_data and hex_data['type'] == 4  # Кислота

    def _sees_resource(self):
        return any(res['amount'] > 0 for res in self.arena.get('food', []))

    def _find_acid_path(self, start_pos, max_op, blocked_hexes):
        # Жадный поиск ближайшей кислоты
        acids = [pos for pos, data in self.grid.items() 
                 if data['type'] == 4 and pos not in blocked_hexes]
        if not acids:
            return self._explore_away_from_hill(start_pos, max_op, blocked_hexes)
        
        # Выбираем ближайшую кислоту по Manhattan distance
        target = min(acids, key=lambda p: self._hex_distance(start_pos, p))
        return self._build_path_to_target(start_pos, target, max_op, blocked_hexes)

    def _explore_away_from_hill(self, start_pos, max_op, blocked_hexes):
        # Движение в сторону от муравейника
        best_pos = start_pos
        best_distance = self._hex_distance(start_pos, self.spot)
        current_pos = start_pos
        remaining_op = max_op
        path = [start_pos]
        
        while remaining_op > 0:
            neighbors = self._get_neighbors(current_pos)
            next_pos = None
            next_cost = None
            
            # Выбираем соседа, максимально удаляющего от муравейника
            for pos in neighbors:
                if pos in blocked_hexes or pos == current_pos:
                    continue
                hex_data = self.grid.get(pos)
                if not hex_data or hex_data['cost'] > remaining_op:
                    continue
                
                distance = self._hex_distance(pos, self.spot)
                if distance > best_distance:
                    best_distance = distance
                    next_pos = pos
                    next_cost = hex_data['cost']
            
            if not next_pos:
                break
                
            path.append(next_pos)
            remaining_op -= next_cost
            current_pos = next_pos
        
        return path

    def _build_path_to_target(self, start, target, max_op, blocked_hexes):
        # Упрощенный поиск пути к цели
        path = [start]
        current = start
        remaining_op = max_op
        
        while current != target and remaining_op > 0:
            neighbors = self._get_neighbors(current)
            next_pos = min(
                neighbors, 
                key=lambda p: self._hex_distance(p, target) if p not in blocked_hexes else float('inf')
            )
            
            if next_pos == current or next_pos in blocked_hexes:
                break
                
            hex_data = self.grid.get(next_pos, {})
            cost = hex_data.get('cost', 1000)
            if cost > remaining_op:
                break
                
            path.append(next_pos)
            remaining_op -= cost
            current = next_pos
            
        return path

    def _hex_distance(self, a, b):
        # Manhattan distance для гексов (odd-r layout)
        return (abs(a[0] - b[0]) + abs(a[0] + a[1] - b[0] - b[1]) + abs(a[1] - b[1])) // 2

    def _get_neighbors(self, pos):
        q, r = pos
        if r % 2 == 1:  # Odd row
            return [
                (q+1, r), (q, r-1), (q-1, r-1),
                (q-1, r), (q-1, r+1), (q, r+1)
            ]
        else:  # Even row
            return [
                (q+1, r), (q+1, r-1), (q, r-1),
                (q-1, r), (q, r+1), (q+1, r+1)
            ]