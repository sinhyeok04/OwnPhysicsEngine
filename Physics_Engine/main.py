import pygame
import sys
import math
from components.solver import Solver
from components.input_handler import InputHandler

WIDTH, HEIGHT = 900, 900
FPS = 120

def get_safe_color(c, a=255):
    return (max(0,min(255,int(c[0]))), max(0,min(255,int(c[1]))), max(0,min(255,int(c[2]))), max(0,min(255,int(a))))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Final Physics Engine")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Consolas", 14)

    solver = Solver(WIDTH, HEIGHT)
    input_handler = InputHandler(solver)
    particle_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    from components.obstacle import RectObstacle
    solver.add_obstacle(RectObstacle(WIDTH/2, HEIGHT - 20, WIDTH, 40))

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        if dt > 0.03: dt = 0.03

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            input_handler.handle_event(event)

        input_handler.handle_input()
        solver.update(dt)

        screen.fill((20, 20, 30))
        particle_surf.fill((0,0,0,0))

        for obs in solver.obstacles:
            obs.draw(screen)

        sleeping_count = 0
        for p in solver.particles:
            if math.isnan(p.pos.x) or math.isnan(p.pos.y): continue
            if not (-1000 < p.pos.x < WIDTH+1000): continue
            
            if p.is_sleeping: sleeping_count += 1

            ix, iy = int(p.pos.x), int(p.pos.y)
            ir = int(p.radius)
            
            if p.type in ["fire", "smoke", "steam", "spark"]:
                alpha = p.life * 255
                col = get_safe_color(p.color, alpha)
                pygame.draw.circle(particle_surf, col, (ix, iy), ir)
            else:
                col = get_safe_color(p.color)
                if p.is_sleeping: col = (col[0]*0.7, col[1]*0.7, col[2]*0.7)
                pygame.draw.circle(screen, col, (ix, iy), ir)
                if not p.is_static:
                    pygame.draw.circle(screen, (0,0,0), (ix, iy), ir, 1)

        screen.blit(particle_surf, (0, 0))

        fps = clock.get_fps()
        
        opt_text = "ON (Spatial Grid)" if solver.use_optimization else "OFF (Brute Force)"
        opt_color = (100, 255, 100) if solver.use_optimization else (255, 100, 100)
        mat_text = input_handler.current_material.upper()
        
        info = [
            (f"FPS         : {fps:.1f}", (255, 255, 255)),
            (f"Particles   : {len(solver.particles)}", (255, 255, 255)),
            (f"Sleeping    : {sleeping_count}", (200, 200, 200)),
            (f"Optimize    : {opt_text}", opt_color),
            ("-" * 28, (150, 150, 150)),
            (f"Material    : {mat_text}", (100, 200, 255)),
            ("Controls:", (255, 255, 0)),
            ("[1-4] Water/Sand/Stone/Fire", (200, 200, 200)),
            ("[Z/X] Wall Shape (Cir/Rect)", (200, 200, 200)),
            ("[L-Click] Spawn Particle", (200, 200, 200)),
            ("[R-Click] Place Wall", (200, 200, 200)),
            ("[G/F] Gravity / Force", (200, 200, 200)),
            ("[O] Toggle Opt / [R] Reset", (200, 200, 200))
        ]
        
        for i, (text, color) in enumerate(info):
            img = font.render(text, True, color)
            screen.blit(img, (20, 20 + i * 18))

        mx, my = pygame.mouse.get_pos()
        pygame.draw.circle(screen, (255, 255, 255), (mx, my), 5, 1)

        if solver.attractor_pos is not None:
             color = (255, 50, 50) if solver.attractor_force < 0 else (50, 255, 50)
             pygame.draw.circle(screen, color, (mx, my), 20, 2)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()