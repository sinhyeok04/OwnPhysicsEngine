import math
import random
from components.grid import SpatialGrid
from components.particle import Particle
from components.vector import Vector2D

class Solver:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.gravity = 1500.0
        
        self.particles = []
        self.obstacles = []
        self.sub_steps = 8
        self.grid = SpatialGrid(width, height, cell_size=12.0)
        self.use_optimization = True 
        
        self.attractor_pos = None
        self.attractor_force = 0

    def spawn_region(self, x, y, p_type, cols=3, rows=3):
        temp = Particle(0, 0, p_type)
        spacing = temp.radius * 2.2
        start_x = x - (cols * spacing) / 2
        start_y = y - (rows * spacing) / 2
        for i in range(cols):
            for j in range(rows):
                px = start_x + i * spacing
                py = start_y + j * spacing
                px += random.uniform(-0.5, 0.5) 
                py += random.uniform(-0.5, 0.5)
                if 0 < px < self.width and 0 < py < self.height:
                    self.add_particle(px, py, p_type)

    def add_particle(self, x, y, p_type, is_static=False):
        p = Particle(x, y, p_type, is_static)
        self.particles.append(p)

    def add_obstacle(self, obs):
        self.obstacles.append(obs)

    def update(self, dt):
        if dt == 0: return
        self.particles = [p for p in self.particles if p.life > 0]
        
        for p in self.particles:
            if p.type == "sand" and p.is_burning and p.burn_timer < 0.1:
                if random.random() < 0.3:
                    self.add_particle(p.pos.x, p.pos.y, "smoke")

        sub_dt = dt / self.sub_steps
        for _ in range(self.sub_steps):
            self.apply_gravity()
            self.apply_forces()
            self.apply_bounds()
            self.solve_collisions()
            self.update_positions(sub_dt)

    def update_positions(self, dt):
        max_vel = 1500.0
        for p in self.particles:
            if p.type in ["sand", "stone"] and not p.is_sleeping and not p.is_static:
                move_sq = (p.pos.x - p.prev_pos.x)**2 + (p.pos.y - p.prev_pos.y)**2
                if move_sq < 0.002: 
                    p.sleep_timer += dt
                    if p.sleep_timer > 0.5: 
                        p.is_sleeping = True
                        p.prev_pos.x = p.pos.x
                        p.prev_pos.y = p.pos.y
                else:
                    p.sleep_timer = 0

            vx = p.pos.x - p.prev_pos.x
            vy = p.pos.y - p.prev_pos.y
            speed = math.sqrt(vx*vx + vy*vy)
            if speed > max_vel * dt:
                ratio = (max_vel * dt) / speed
                p.prev_pos.x = p.pos.x - vx * ratio
                p.prev_pos.y = p.pos.y - vy * ratio
            
            p.update_position(dt)
            if not (-1000 < p.pos.x < self.width + 1000 and -1000 < p.pos.y < self.height + 1000):
                p.life = 0

    def apply_gravity(self):
        for p in self.particles:
            if p.is_static or p.is_sleeping: continue
            
            if p.type in ["fire", "smoke", "steam"]:
                p.acc.x += random.uniform(-20, 20)
                p.acc.y += self.gravity * p.mass
            else:
                p.acc.y += self.gravity * p.mass

    def apply_forces(self):
        if self.attractor_pos is None: return
        tx, ty = self.attractor_pos.x, self.attractor_pos.y
        for p in self.particles:
            if p.is_static: continue
            p.wake_up()
            dx = tx - p.pos.x
            dy = ty - p.pos.y
            dist_sq = dx*dx + dy*dy
            if dist_sq > 100:
                dist = math.sqrt(dist_sq)
                f = self.attractor_force / dist
                p.acc.x += (dx/dist) * f
                p.acc.y += (dy/dist) * f

    def apply_bounds(self):
        w, h = self.width, self.height
        for p in self.particles:
            if p.is_static or p.is_sleeping: continue
            if p.pos.y > h - p.radius:
                p.pos.y = h - p.radius
                f = 0.9 if p.type in ["sand", "stone"] else 0.05
                p.prev_pos.x += (p.pos.x - p.prev_pos.x) * f
                p.prev_pos.y = p.pos.y 
            if p.pos.x < p.radius:
                p.pos.x = p.radius
                p.prev_pos.x = p.pos.x
            elif p.pos.x > w - p.radius:
                p.pos.x = w - p.radius
                p.prev_pos.x = p.pos.x

    def resolve_interaction(self, p1, p2):
        t1, t2 = p1.type, p2.type
        if (t1 == "water" and t2 == "fire") or (t1 == "fire" and t2 == "water"):
            fire = p1 if t1 == "fire" else p2
            water = p1 if t1 == "water" else p2
            fire.life = 0
            if random.random() < 0.2:
                water.type = "steam"
                water.set_type_properties("steam")
                water.wake_up()
            return True
        if (t1 == "sand" and t2 == "fire") or (t1 == "fire" and t2 == "sand"):
            sand = p1 if t1 == "sand" else p2
            fire = p1 if t1 == "fire" else p2
            if not sand.is_burning:
                sand.is_burning = True
                sand.burn_timer = 2.0 + random.uniform(0, 1.0)
                sand.max_burn_time = sand.burn_timer
                sand.wake_up()
            fire.life = 0
            return True
        if t1 == "sand" and t2 == "sand":
            if p1.is_burning and not p2.is_burning:
                if random.random() < 0.005:
                    p2.is_burning = True
                    p2.burn_timer = 2.0 + random.uniform(0, 1.0)
                    p2.max_burn_time = p2.burn_timer
                    p2.wake_up()
            elif p2.is_burning and not p1.is_burning:
                if random.random() < 0.005:
                    p1.is_burning = True
                    p1.burn_timer = 2.0 + random.uniform(0, 1.0)
                    p1.max_burn_time = p1.burn_timer
                    p1.wake_up()
            return False
        return False

    def solve_collisions(self):
        if self.use_optimization:
            self.grid.clear()
            for i, p in enumerate(self.particles):
                self.grid.add_particle(i, p.pos.x, p.pos.y)

        for p in self.particles:
            if p.is_sleeping: continue
            for obs in self.obstacles:
                obs.resolve_collision(p)

        count = len(self.particles)
        if not self.use_optimization:
            for i in range(count):
                p1 = self.particles[i]
                for j in range(i + 1, count):
                    self.check_collision(p1, self.particles[j])
        else:
            for i in range(count):
                p1 = self.particles[i]
                candidates = self.grid.get_potential_collisions(p1.pos.x, p1.pos.y)
                for j in candidates:
                    if i < j: self.check_collision(p1, self.particles[j])

    def check_collision(self, p1, p2):
        if (p1.is_sleeping and p2.is_sleeping): return
        if (p1.is_static and p2.is_static): return

        if self.resolve_interaction(p1, p2): return

        p1_gas = p1.type in ["fire", "smoke", "steam"]
        p2_gas = p2.type in ["fire", "smoke", "steam"]
        if p1_gas and p2_gas: return

        dx = p1.pos.x - p2.pos.x
        dy = p1.pos.y - p2.pos.y
        dist_sq = dx*dx + dy*dy
        min_dist = p1.radius + p2.radius
        
        if dist_sq < min_dist * min_dist and dist_sq > 0.0001:
            dist = math.sqrt(dist_sq)
            n_x, n_y = dx/dist, dy/dist
            delta = min_dist - dist
            
            if p1.is_sleeping: p1.wake_up()
            if p2.is_sleeping: p2.wake_up()

            w1 = 0 if p1.is_static else 1/p1.mass
            w2 = 0 if p2.is_static else 1/p2.mass
            total_w = w1 + w2
            if total_w == 0: return

            r1 = w1 / total_w
            r2 = w2 / total_w
            
            if p1_gas: r1, r2 = 1.0, 0.0
            elif p2_gas: r1, r2 = 0.0, 1.0

            response_coef = 0.3
            move_x = n_x * delta * response_coef
            move_y = n_y * delta * response_coef
            
            if not p1.is_static:
                p1.pos.x += move_x * r1
                p1.pos.y += move_y * r1
            if not p2.is_static:
                p2.pos.x -= move_x * r2
                p2.pos.y -= move_y * r2

            if not p1_gas and not p2_gas:
                friction = 0.05
                tx, ty = -n_y, n_x
                v1x = p1.pos.x - p1.prev_pos.x
                v1y = p1.pos.y - p1.prev_pos.y
                v2x = p2.pos.x - p2.prev_pos.x
                v2y = p2.pos.y - p2.prev_pos.y
                vt1 = v1x * tx + v1y * ty
                vt2 = v2x * tx + v2y * ty
                f_strength = friction * 0.1
                if not p1.is_static:
                    p1.prev_pos.x += tx * vt1 * f_strength
                    p1.prev_pos.y += ty * vt1 * f_strength
                if not p2.is_static:
                    p2.prev_pos.x += tx * vt2 * f_strength
                    p2.prev_pos.y += ty * vt2 * f_strength