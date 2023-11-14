class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.x_pos = x
        self.y_pos = y
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        screen.blit(self.image, self.rect)