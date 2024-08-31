from pygame.math import Vector2


def clip(value: float, min_value: float, max_value: float) -> float:
    if value > max_value:
        return max_value
    
    if value < min_value:
        return min_value
    
    return value


def vector2tuple(value: Vector2) -> tuple[int, int]:
    return int(value.x), int(value.y)


def min_vector(vector_a: Vector2, vector_b: Vector2) -> Vector2:
    return Vector2(min(vector_a.x, vector_b.x), min(vector_a.y, vector_b.y))


def max_vector(vector_a: Vector2, vector_b: Vector2) -> Vector2:
    return Vector2(max(vector_a.x, vector_b.x), max(vector_a.y, vector_b.y))


def clip_vector(vector: Vector2, min_value: Vector2, max_value: Vector2) -> Vector2:
    return Vector2(
        clip(vector.x, min_value.x, max_value.x), 
        clip(vector.y, min_value.y, max_value.y)
    )


def round_vector(vector: Vector2) -> Vector2:
    return Vector2(round(vector.x), round(vector.y))
