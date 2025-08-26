from math import pi, atan2, cos, sin, inf, sqrt
from templates import UNISTROKES

RESAMPLE_SIZE= 16
ORIGIN = (0, 0)
SQUARE_SIZE = 350
half_diagonal = 0.5 * sqrt(SQUARE_SIZE**2 + SQUARE_SIZE**2)
ANGLE_RANGE = (2 / 180) * pi
ANGLE_PRECISION = (2 / 180) * pi
PHI = 0.5 * (-1.0 + (5.0)**0.5)


class Dollar:

    def __init__(self):
        # format the example gestures
        self.unistrokes = []
        for template in UNISTROKES:
            self.unistrokes.append(Stroke(template[1]))
            self.unistrokes[-1].name = template[0]

    def get_gesture(self, points):
        stroke = Stroke(points)
         # search for the closest gesture (ie. with minimal distance)
        min_distance = inf
        gesture_name = ''
        for template_stroke in self.unistrokes:
            distance = stroke.distance_at_best_angle(template_stroke.points)
            if distance < min_distance:
                # update the current best gesture
                min_distance = distance
                gesture_name = template_stroke.name
        confidence =  max(0, 1 - (min_distance / half_diagonal))
        return gesture_name, confidence

class Stroke:

    def __init__(self, points , should_format=True):
        self.points = points
        if should_format:
            self.resample() # 重採樣:將手勢軌跡調整成固定數量的點
            self.rotate_by(-self.indicative_angle()) # 旋轉
            self.scale_to(SQUARE_SIZE) # 縮放
            self.translate_to(ORIGIN) # 平移

    def resample(self):
        points = self.points
        I = self.path_length() / (RESAMPLE_SIZE - 1) # Average distsnace
        D = 0 # 當前距離累積
        new_points = [points[0]]
        i = 1
        while i < len(points):
            previous, current = points[i - 1:i + 1] # (point[i-1],point[i])
            d = distance(previous, current)
            if ((D + d) >= I): # Insert new point between previous and current 
                q = (previous[0] + ((I - D) / d) * (current[0] - previous[0]),
                     previous[1] + ((I - D) / d) * (current[1] - previous[1]))
                # append new point 'q'
                new_points.append(q)
                # insert 'q' at position i in points s.t. 'q' will be the next i
                points.insert(i, q)
                D = 0
            else:
                D += d
            i += 1
        # somtimes we fall a rounding-error short of adding the last point, so
        # add it if so
        if len(new_points) == RESAMPLE_SIZE - 1:
            new_points.append(new_points[-1])
        self.points = new_points

    def path_length(self):
        d = 0
        for i in range(1, len(self.points)):
            d += distance(self.points[i - 1], self.points[i])
        return d

    def indicative_angle(self):
        # 計算Central point至starting point的角度
        # angle formed by (points[0], centroid) and the horizon
        c = self.centroid()
        return atan2(c[1] - self.points[0][1], c[0] - self.points[0][0])

    def centroid(self):
        n = len(self.points)
        return (
            sum([p[0] / n for p in self.points]),
            sum([p[1] / n for p in self.points])
        )

    def rotate_by(self, angle):
        c = self.centroid()
        new_points = []
        for p in self.points:
            dx, dy = p[0] - c[0], p[1] - c[1]
            new_points.append((
                dx * cos(angle) - dy * sin(angle) + c[0],
                dx * sin(angle) + dy * cos(angle) + c[1]
            ))
        self.points = new_points

    def scale_to(self, size):
        B = self.bounding_box()
        new_points = []
        for p in self.points:
            new_points.append((
                p[0] * size / B[0] if B[0] != 0 else p[0],
                p[1] * size / B[1] if B[1] != 0 else p[1]
            ))
        self.points = new_points

    def bounding_box(self):
        # 計算包含所有點的最小矩形(框)
        minX, maxX = inf, -inf
        minY, maxY = inf, -inf
        for point in self.points:
            minX, maxX = min(minX, point[0]), max(maxX, point[0])
            minY, maxY = min(minY, point[1]), max(maxY, point[1])
        return (maxX - minX, maxY - minY)

    def translate_to(self, target):
        c = self.centroid()
        new_points = []
        for p in self.points:
            new_points.append((
                p[0] + target[0] - c[0], #中心移動到origin point
                p[1] + target[1] - c[1]
            ))
        self.points = new_points

    def distance_at_best_angle(self, T):
        a = -ANGLE_RANGE
        b = ANGLE_RANGE
        x1 = PHI * a + (1 - PHI) * b
        x2 = PHI * b + (1 - PHI) * a
        f1 = self.distance_at_angle(T, x1)
        f2 = self.distance_at_angle(T, x2)
        while abs(b - a) > ANGLE_PRECISION:
            if f1 < f2:
                b = x2
                x2 = x1
                f2 = f1
                x1 = PHI * a + (1 * PHI) * b
                f1 = self.distance_at_angle(T, x1)
            else:
                a = x1
                x1 = x2
                f1 = f2
                x2 = PHI * b + (1 - PHI) * a
                f2 = self.distance_at_angle(T, x2)
        return min(f1, f2)

    def distance_at_angle(self, T, angle):
        rotated_stroke = Stroke(self.points, False) # 複製當前point
        rotated_stroke.rotate_by(angle)
        return rotated_stroke.path_distance(T)

    def path_distance(self, points):
        n = len(points)
        return sum([distance(self.points[i], points[i]) / n for i in range(n)])

def distance(p1, p2):
    return ((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)**0.5
