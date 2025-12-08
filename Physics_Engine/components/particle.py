from components.vector import Vector2D

class Particle:
    def __init__(self, x, y, p_type="water", is_static=False):
        self.pos = Vector2D(x, y)
        self.prev_pos = Vector2D(x, y)
        self.acc = Vector2D(0, 0)
        self.type = p_type
        self.is_static = is_static
        
        self.is_sleeping = False
        self.sleep_timer = 0.0

        # 기본값
        self.radius = 4.0
        self.mass = 1.0
        self.friction = 0.0
        self.color = (255, 255, 255)
        self.life = 1.0
        self.decay = 0.0
        
        self.is_burning = False
        self.burn_timer = 0.0
        self.max_burn_time = 0.0
        
        self.set_type_properties(p_type)

    def set_type_properties(self, p_type):
        if p_type == "water":
            self.radius = 3.0
            self.mass = 1.0
            self.friction = 0.0
            self.color = (30, 100, 250)
            
        elif p_type == "sand":
            self.radius = 4.0
            self.mass = 2.0
            self.friction = 1.0
            self.color = (230, 190, 60)
            
        elif p_type == "stone":
            self.radius = 6.0
            self.mass = 8.0
            self.friction = 0.9
            self.color = (100, 100, 100)
            
        elif p_type == "fire":
            self.radius = 4.0
            self.mass = -0.8
            self.friction = 0.1
            self.decay = 0.015
            self.color = (255, 80, 10)
            
        elif p_type == "smoke":
            self.radius = 5.5
            self.mass = -0.05
            self.friction = 0.1
            self.decay = 0.01
            self.color = (150, 150, 150)
            
        elif p_type == "steam":
            self.radius = 5.0
            self.mass = -0.8
            self.friction = 0.1
            self.decay = 0.005
            self.color = (200, 240, 255)

    def apply_force(self, force):
        if not self.is_static and not self.is_sleeping:
            self.acc += force

    def wake_up(self):
        self.is_sleeping = False
        self.sleep_timer = 0

    def update_position(self, dt):
        if self.is_static or self.is_sleeping: return

        vx = self.pos.x - self.prev_pos.x
        vy = self.pos.y - self.prev_pos.y
        
        self.prev_pos.x = self.pos.x
        self.prev_pos.y = self.pos.y
        
        damping = 0.98 if self.type in ["fire", "smoke", "steam"] else 1.0
        
        self.pos.x += vx * damping + self.acc.x * dt * dt
        self.pos.y += vy * damping + self.acc.y * dt * dt
        
        self.acc = Vector2D(0, 0)
        
        if self.decay > 0:
            self.life -= self.decay

        if self.is_burning:
            self.burn_timer -= dt
            p = 0
            if self.max_burn_time > 0:
                p = self.burn_timer / self.max_burn_time
            
            if p > 0.6: self.color = (255, 150, 0)
            elif p > 0.3: self.color = (100, 20, 0)
            else: self.color = (50, 50, 50)

            if self.burn_timer <= 0:
                self.life = 0