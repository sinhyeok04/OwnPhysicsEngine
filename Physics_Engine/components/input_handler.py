import pygame
import math
from components.obstacle import CircleObstacle, RectObstacle

class InputHandler:
    def __init__(self, solver):
        self.solver = solver
        self.current_material = "water"
        self.obs_type = "circle" 

    def handle_input(self):
        mx, my = pygame.mouse.get_pos()
        buttons = pygame.mouse.get_pressed()
        keys = pygame.key.get_pressed()

        if keys[pygame.K_1]: self.current_material = "water"
        if keys[pygame.K_2]: self.current_material = "sand"
        if keys[pygame.K_3]: self.current_material = "stone"
        if keys[pygame.K_4]: self.current_material = "fire"

        if keys[pygame.K_z]: self.obs_type = "circle"
        if keys[pygame.K_x]: self.obs_type = "rect"

        if keys[pygame.K_g]:
            self.solver.attractor_pos = self.solver.get_vector(mx, my)
            self.solver.attractor_force = 250000.0
        elif keys[pygame.K_f]:
            self.solver.attractor_pos = self.solver.get_vector(mx, my)
            self.solver.attractor_force = -250000.0
        else:
            self.solver.attractor_pos = None

        if buttons[0]:
            cols, rows = 3, 3
            if self.current_material == "fire": cols, rows = 2, 2
            self.solver.spawn_region(mx, my, self.current_material, cols, rows)

        if buttons[2]:
            can_place = True
            for obs in self.solver.obstacles:
                dist = math.hypot(obs.pos.x - mx, obs.pos.y - my)
                if dist < 20: 
                    can_place = False
                    break
            
            if can_place:
                if self.obs_type == "circle":
                    self.solver.add_obstacle(CircleObstacle(mx, my, 30))
                elif self.obs_type == "rect":
                    self.solver.add_obstacle(RectObstacle(mx, my, 60, 30))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: 
                self.solver.particles = []
                self.solver.obstacles = []
            
            elif event.key == pygame.K_o: 
                self.solver.use_optimization = not self.solver.use_optimization