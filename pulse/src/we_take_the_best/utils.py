def get_neighbors(q, r):
    """Возвращает соседние гексы для заданных координат (odd-r схема)"""
    directions = [
        [(1, 0), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)],  # Четные строки
        [(1, 0), (1, -1), (0, -1), (-1, 0), (0, 1), (1, 1)]     # Нечетные строки
    ]
    parity = r & 1
    return [(q + dq, r + dr) for dq, dr in directions[parity]]

def hex_distance(a, b):
    """Вычисляет расстояние между двумя гексами"""
    return (abs(a[0] - b[0]) + abs(a[0] + a[1] - b[0] - b[1]) + abs(a[1] - b[1])) // 2

def direction_score(pos, target):
    """Оценка направления движения к цели"""
    return hex_distance(pos, target)