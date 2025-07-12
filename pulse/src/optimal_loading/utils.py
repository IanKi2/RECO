def get_neighbors(q, r):
    directions = [
        [(1, 0), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)],
        [(1, 0), (1, -1), (0, -1), (-1, 0), (0, 1), (1, 1)]
    ]
    parity = r & 1
    return [(q + dq, r + dr) for dq, dr in directions[parity]]

def hex_distance(a, b):
    return (abs(a[0] - b[0]) + abs(a[0] + a[1] - b[0] - b[1]) + abs(a[1] - b[1])) // 2

def direction_score(pos, target):
    return hex_distance(pos, target)