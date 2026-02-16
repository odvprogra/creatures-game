class Camera:
    def __init__(self, base_scale: int = 8):
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0
        self.zoom: float = 1.0
        self.base_scale: int = base_scale

    def world_to_screen(self, wx: float, wy: float) -> tuple[int, int]:
        sx = int((wx - self.offset_x) * self.zoom * self.base_scale)
        sy = int((wy - self.offset_y) * self.zoom * self.base_scale)
        return sx, sy

    def screen_to_world(self, sx: int, sy: int) -> tuple[float, float]:
        wx = sx / (self.zoom * self.base_scale) + self.offset_x
        wy = sy / (self.zoom * self.base_scale) + self.offset_y
        return wx, wy

    def zoom_at(self, mouse_sx: int, mouse_sy: int, factor: float):
        wx, wy = self.screen_to_world(mouse_sx, mouse_sy)
        self.zoom *= factor
        self.zoom = max(0.2, min(self.zoom, 10.0))
        self.offset_x = wx - mouse_sx / (self.zoom * self.base_scale)
        self.offset_y = wy - mouse_sy / (self.zoom * self.base_scale)

    def pan(self, dx_screen: int, dy_screen: int):
        self.offset_x -= dx_screen / (self.zoom * self.base_scale)
        self.offset_y -= dy_screen / (self.zoom * self.base_scale)
