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

def bresenham_line_3d(start: tuple, end: tuple) -> list:
    points = []
    x0, y0, z0 = start
    x1, y1, z1 = end

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    dz = abs(z1 - z0)

    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    sz = 1 if z0 < z1 else -1

    if dx >= dy and dx >= dz:
        err1 = 2 * dy - dx
        err2 = 2 * dz - dx
        while x0 != x1:
            points.append((x0, y0, z0))
            if err1 > 0:
                y0 += sy
                err1 -= 2 * dx
            if err2 > 0:
                z0 += sz
                err2 -= 2 * dx
            err1 += 2 * dy
            err2 += 2 * dz
            x0 += sx

    elif dy >= dx and dy >= dz:
        err1 = 2 * dx - dy
        err2 = 2 * dz - dy
        while y0 != y1:
            points.append((x0, y0, z0))
            if err1 > 0:
                x0 += sx
                err1 -= 2 * dy
            if err2 > 0:
                z0 += sz
                err2 -= 2 * dy
            err1 += 2 * dx
            err2 += 2 * dz
            y0 += sy

    else:
        err1 = 2 * dy - dz
        err2 = 2 * dx - dz
        while z0 != z1:
            points.append((x0, y0, z0))
            if err1 > 0:
                y0 += sy
                err1 -= 2 * dz
            if err2 > 0:
                x0 += sx
                err2 -= 2 * dz
            err1 += 2 * dy
            err2 += 2 * dx
            z0 += sz

    points.append((x0, y0, z0))

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
    