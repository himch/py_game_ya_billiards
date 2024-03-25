import math


class Point:
    """
    Класс описывает точку на плоскости
    """
    def __init__(self, point_t=(0, 0)):
        self.x = float(point_t[0])
        self.y = float(point_t[1])

    def __add__(self, other):
        return Point((self.x + other.x, self.y + other.y))

    def __sub__(self, other):
        return Point((self.x - other.x, self.y - other.y))

    def __mul__(self, scalar):
        return Point((self.x * scalar, self.y * scalar))

    def __truediv__(self, scalar):
        return Point((self.x / scalar, self.y / scalar))

    def __len__(self):
        return 2

    def __getitem__(self, key):
        return self.y if key % 2 else self.x

    def __iter__(self):
        yield self.x
        yield self.y

    def __str__(self):
        return str((self.x, self.y))

    def get(self):
        return self.x, self.y

    def length(self):
        return int(math.sqrt(self.x ** 2 + self.y ** 2))


class Vector:
    """
    Класс описывает отрезок на плоскости
    """
    def __init__(self, vector: (Point, Point)):
        self.start = vector[0]
        self.end = vector[1]

    def __len__(self):
        return 2

    def __getitem__(self, key):
        return self.end if key % 2 else self.start

    def __iter__(self):
        yield self.start
        yield self.end

    def __str__(self):
        return str((self.start, self.end))

    def length(self):
        return math.sqrt((self.end.x - self.start.x) ** 2 + (self.end.y - self.start.y) ** 2)


def make_vector(start_point: Point, aiming_point: Point, length: float) -> Vector:
    """
    Создает отрезок из точки start_point через точку aiming_point длины length
    :param start_point:
    :param aiming_point:
    :param length:
    :return:
    """
    if aiming_point.x != start_point.x:
        k = (aiming_point.y - start_point.y) / (aiming_point.x - start_point.x)
        alpha = math.atan(k)
        b = length * math.cos(alpha)
        a = b * k
        direction = -1 if start_point.x > aiming_point.x else 1
    else:
        # вертикальная прямая
        b = 0
        a = length
        direction = -1 if start_point.y > aiming_point.y else 1

    x2 = start_point.x + b * direction
    y2 = start_point.y + a * direction
    return Vector((start_point, Point((x2, y2))))


def intersect(line_1: Vector, line_2: Vector) -> [Point, None]:
    """
    Возвращает точку пересечения двух отрезков на плоскости
    :param line_1: первый отрезок
    :param line_2: второй отрезок
    :return:  Точка пересечения отрезков или None
    """
    (x1, y1), (x2, y2) = line_1
    (x3, y3), (x4, y4) = line_2

    if (x1 != x2) and (x3 != x4):
        k1 = (y1 - y2) / (x1 - x2)
        b1 = y1 - k1 * x1
        k2 = (y3 - y4) / (x3 - x4)
        b2 = y3 - k2 * x3
        if k1 != k2:
            x = (b2 - b1) / (k1 - k2)
            y = (k2 * b1 - k1 * b2) / (k2 - k1)
            if (min(x1, x2) <= x <= max(x1, x2)) and (min(x3, x4) <= x <= max(x3, x4)) and (
                    min(y1, y2) <= y <= max(y1, y2)) and (min(y3, y4) <= y <= max(y3, y4)):
                return Point((x, y))
            else:
                return None
        else:
            if b1 == b2:
                if max(min(x1, x2), min(x3, x4)) < min(max(x1, x2), max(x3, x4)):
                    # multiple solution
                    return Point((max(min(x1, x2), min(x3, x4)), max(min(y1, y2), min(y3, y4))))
                    # min(max(x1,x2),max(x3,x4)), min(max(y1,y2),max(y3,y4))
                else:
                    if max(min(x1, x2), min(x3, x4)) == min(max(x1, x2), max(x3, x4)):
                        return Point((max(min(x1, x2), min(x3, x4)), max(min(y1, y2), min(y3, y4))))
                    else:
                        return None
            else:
                return None
    else:
        if ((x1 == x2) and (x3 != x4)) or ((x1 != x2) and (x3 == x4)):
            k = x = b = 0
            if x3 != x4:
                k = (y3 - y4) / (x3 - x4)
                b = y3 - k * x3
                x = x1
            if x1 != x2:
                k = (y1 - y2) / (x1 - x2)
                b = y1 - k * x1
                x = x3
            y = k * x + b
            if (min(x1, x2) <= x <= max(x1, x2)) and (min(x3, x4) <= x <= max(x3, x4)) and (
                    min(y1, y2) <= y <= max(y1, y2)) and (min(y3, y4) <= y <= max(y3, y4)):
                return Point((x, y))
            else:
                return None
        else:
            if (x1 == x2) and (x3 == x4) and (x1 == x3):
                if max(min(y1, y2), min(y3, y4)) < min(max(y1, y2), max(y3, y4)):
                    # multiple solution
                    return Point((x1, max(min(y1, y2), min(y3, y4))))
                    # min(max(y1, y2), max(y3, y4))
                else:
                    if max(min(y1, y2), min(y3, y4)) == min(max(y1, y2), max(y3, y4)):
                        return Point((x1, max(min(y1, y2), min(y3, y4))))
                    else:
                        return None
            else:
                return None
