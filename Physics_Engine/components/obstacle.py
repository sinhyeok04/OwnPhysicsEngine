import math
import pygame
from components.vector import Vector2D

class Obstacle:
    def __init__(self, x, y, color=(120, 120, 120)):
        self.pos = Vector2D(x, y)
        self.color = color
        self.angle = 0.0

    def draw(self, screen):
        pass

    def resolve_collision(self, p):
        pass

class CircleObstacle(Obstacle):
    def __init__(self, x, y, radius):
        super().__init__(x, y)
        self.radius = radius

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)
        pygame.draw.circle(screen, (200, 200, 200), (int(self.pos.x), int(self.pos.y)), self.radius, 2)

    def resolve_collision(self, p):
        dx = p.pos.x - self.pos.x
        dy = p.pos.y - self.pos.y
        dist_sq = dx*dx + dy*dy
        min_dist = self.radius + p.radius
        
        if dist_sq < min_dist * min_dist:
            dist = math.sqrt(dist_sq)
            if dist == 0: return
            
            n_x, n_y = dx / dist, dy / dist
            overlap = min_dist - dist
            
            p.pos.x += n_x * overlap
            p.pos.y += n_y * overlap
            
            friction = 0.1 if p.type == "water" else 0.8
            p.prev_pos.x += (p.pos.x - p.prev_pos.x) * friction * 0.1
            p.prev_pos.y += (p.pos.y - p.prev_pos.y) * friction * 0.1

class RectObstacle(Obstacle):
    def __init__(self, x, y, w, h):
        super().__init__(x, y)
        self.w = w
        self.h = h

    def draw(self, screen):
        rect = pygame.Rect(int(self.pos.x - self.w/2), int(self.pos.y - self.h/2), self.w, self.h)
        pygame.draw.rect(screen, self.color, rect)
        pygame.draw.rect(screen, (200, 200, 200), rect, 2)

    def resolve_collision(self, p):
        left = self.pos.x - self.w/2 - p.radius
        right = self.pos.x + self.w/2 + p.radius
        top = self.pos.y - self.h/2 - p.radius
        bottom = self.pos.y + self.h/2 + p.radius

        if left < p.pos.x < right and top < p.pos.y < bottom:
            dl = p.pos.x - left
            dr = right - p.pos.x
            dt = p.pos.y - top
            db = bottom - p.pos.y
            
            m = min(dl, dr, dt, db)
            
            if m == dl: p.pos.x = left
            elif m == dr: p.pos.x = right
            elif m == dt: p.pos.y = top
            elif m == db: p.pos.y = bottom
            
            friction = 0.1 if p.type == "water" else 0.8
            p.prev_pos.x += (p.pos.x - p.prev_pos.x) * friction * 0.1
            p.prev_pos.y += (p.pos.y - p.prev_pos.y) * friction * 0.1