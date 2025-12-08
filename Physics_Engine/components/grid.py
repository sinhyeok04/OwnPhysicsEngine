class SpatialGrid:
    def __init__(self, width, height, cell_size):
        self.cell_size = cell_size
        self.cols = int(width / cell_size) + 1
        self.rows = int(height / cell_size) + 1
        self.cells = {}

    def clear(self):
        self.cells = {}

    def get_key(self, x, y):
        cx = int(x / self.cell_size)
        cy = int(y / self.cell_size)
        return (cx, cy)

    def add_particle(self, index, x, y):
        key = self.get_key(x, y)
        if key not in self.cells:
            self.cells[key] = []
        self.cells[key].append(index)

    def get_potential_collisions(self, x, y):
        cx = int(x / self.cell_size)
        cy = int(y / self.cell_size)
        
        candidates = []
        
        # 주변 9개 셀(3x3) 검사
        for i in range(-1, 2):
            for j in range(-1, 2):
                key = (cx + i, cy + j)
                if key in self.cells:
                    candidates.extend(self.cells[key])
                    
        return candidates