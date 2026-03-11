import pygame
import random
import math
import config


class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.heading = 0
        self.speed = config.ROBOT_SPEED
        self.turn_speed = config.ROBOT_TURN_SPEED
        self.size = config.ROBOT_SIZE
        self.path = []
        
    def update(self, command):
        if command == 'forward':
            rad = math.radians(self.heading)
            self.x += self.speed * math.cos(rad)
            self.y += self.speed * math.sin(rad)
        elif command == 'back':
            rad = math.radians(self.heading)
            self.x -= self.speed * math.cos(rad)
            self.y -= self.speed * math.sin(rad)
        elif command == 'left':
            self.heading -= self.turn_speed
            # DON'T move forward while turning - just turn!
        elif command == 'right':
            self.heading += self.turn_speed
            # DON'T move forward while turning - just turn!
        
        if len(self.path) == 0 or (int(self.x), int(self.y)) != self.path[-1]:
            self.path.append((int(self.x), int(self.y)))
            if len(self.path) > 200:
                self.path.pop(0)
    
    def draw(self, screen):
        if len(self.path) > 1:
            pygame.draw.lines(screen, (100, 200, 255), False, self.path, 2)
        pygame.draw.circle(screen, (0, 150, 255), (int(self.x), int(self.y)), self.size)
        rad = math.radians(self.heading)
        end_x = self.x + self.size * math.cos(rad)
        end_y = self.y + self.size * math.sin(rad)
        pygame.draw.line(screen, (255, 255, 255), (self.x, self.y), (end_x, end_y), 3)
    
    def get_position(self):
        return (self.x, self.y)
    
    def get_bounds(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)


class Car:
    def __init__(self, x, y, direction='horizontal'):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = random.uniform(1.5, 3.0)
        self.width = 40
        self.height = 20
        self.color = (random.randint(100, 255), random.randint(0, 100), 0)
        
    def update(self, width, height):
        if self.direction == 'horizontal':
            self.x += self.speed
            if self.x > width + 50:
                self.x = -50
        else:
            self.y += self.speed
            if self.y > height + 50:
                self.y = -50
    
    def draw(self, screen):
        if self.direction == 'horizontal':
            rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2, self.width, self.height)
        else:
            rect = pygame.Rect(self.x - self.height//2, self.y - self.width//2, self.height, self.width)
        pygame.draw.rect(screen, self.color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)
    
    def get_position(self):
        return (self.x, self.y)
    
    def get_velocity(self):
        if self.direction == 'horizontal':
            return (self.speed, 0)
        return (0, self.speed)
    
    def get_bounds(self):
        if self.direction == 'horizontal':
            return pygame.Rect(self.x - self.width//2, self.y - self.height//2, self.width, self.height)
        return pygame.Rect(self.x - self.height//2, self.y - self.width//2, self.height, self.width)


class Pedestrian:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.size = 8
        self.wander_timer = 0
        
    def update(self, width, height):
        self.wander_timer -= 1
        if self.wander_timer <= 0:
            self.vx = random.uniform(-1, 1)
            self.vy = random.uniform(-1, 1)
            self.wander_timer = random.randint(30, 120)
        
        self.x += self.vx
        self.y += self.vy
        
        if self.x < 50 or self.x > width - 50:
            self.vx *= -1
        if self.y < 50 or self.y > height - 50:
            self.vy *= -1
    
    def draw(self, screen):
        pygame.draw.circle(screen, (255, 100, 100), (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x), int(self.y)), self.size, 1)
    
    def get_position(self):
        return (self.x, self.y)
    
    def get_bounds(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)


class Obstacle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
    def draw(self, screen):
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, (100, 100, 100), rect)
        pygame.draw.rect(screen, (50, 50, 50), rect, 2)
    
    def get_bounds(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Destination:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 25
        self.pulse = 0
        
    def update(self):
        self.pulse = (self.pulse + 0.1) % (2 * math.pi)
    
    def draw(self, screen):
        pulse_size = self.size + int(5 * math.sin(self.pulse))
        pygame.draw.circle(screen, (0, 255, 0), (int(self.x), int(self.y)), pulse_size, 3)
        pygame.draw.circle(screen, (0, 255, 0), (int(self.x), int(self.y)), 5)
    
    def get_position(self):
        return (self.x, self.y)
    
    def check_reached(self, robot_pos):
        dx = robot_pos[0] - self.x
        dy = robot_pos[1] - self.y
        return math.sqrt(dx*dx + dy*dy) < self.size
