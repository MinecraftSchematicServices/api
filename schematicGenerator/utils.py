import mcschematic


def points_to_scheme(points, block):
    schem = mcschematic.MCSchematic()
    for point in points:
        schem.setBlock(point, block)
    return schem

def bresenham_line_2d(start: tuple, end: tuple) -> list:
    points = []
    x0, y0 = start
    x1, y1 = end
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
    return points


def surface(pos_1: tuple, pos_2: tuple) -> list:
    min_x = min(pos_1[0], pos_2[0])
    max_x = max(pos_1[0], pos_2[0])
    min_y = min(pos_1[1], pos_2[1])
    max_y = max(pos_1[1], pos_2[1])
    return [(x, y) for x in range(min_x, max_x + 1) for y in range(min_y, max_y + 1)]

def volume(pos_1: tuple, pos_2: tuple) -> list:
    min_x = min(pos_1[0], pos_2[0])
    max_x = max(pos_1[0], pos_2[0])
    min_y = min(pos_1[1], pos_2[1])
    max_y = max(pos_1[1], pos_2[1])
    min_z = min(pos_1[2], pos_2[2])
    max_z = max(pos_1[2], pos_2[2])
    return [(x, y, z) for x in range(min_x, max_x + 1) for y in range(min_y, max_y + 1) for z in range(min_z, max_z + 1)]
    