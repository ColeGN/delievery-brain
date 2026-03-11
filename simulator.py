import pygame
import sys
import math
import random
import config
from brain import GeminiNavigator
from entities import Robot, Car, Pedestrian, Obstacle, Destination


class Environment:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.robot = Robot(100, height // 2)
        self.cars = []
        self.pedestrians = []
        self.obstacles = []
        self.destination = Destination(*config.DESTINATION)
        
        for i in range(3):
            y = 150 + i * 200
            for j in range(3):
                x = random.randint(-100, width)
                self.cars.append(Car(x, y, 'horizontal'))
        
        for i in range(2):
            x = 300 + i * 300
            for j in range(2):
                y = random.randint(-100, height)
                self.cars.append(Car(x, y, 'vertical'))
        
        for _ in range(8):
            x = random.randint(50, width - 50)
            y = random.randint(50, height - 50)
            self.pedestrians.append(Pedestrian(x, y))
        
        self.obstacles.append(Obstacle(200, 50, 80, 80))
        self.obstacles.append(Obstacle(500, 200, 100, 60))
        self.obstacles.append(Obstacle(350, 450, 120, 80))
        self.obstacles.append(Obstacle(700, 100, 60, 150))
        
    def update(self):
        for car in self.cars:
            car.update(self.width, self.height)
        for pedestrian in self.pedestrians:
            pedestrian.update(self.width, self.height)
        self.destination.update()
    
    def draw(self, screen):
        road_color = (60, 60, 60)
        for i in range(3):
            y = 150 + i * 200
            pygame.draw.rect(screen, road_color, (0, y - 30, self.width, 60))
        for i in range(2):
            x = 300 + i * 300
            pygame.draw.rect(screen, road_color, (x - 30, 0, 60, self.height))
        
        for obstacle in self.obstacles:
            obstacle.draw(screen)
        for car in self.cars:
            car.draw(screen)
        for pedestrian in self.pedestrians:
            pedestrian.draw(screen)
        
        self.destination.draw(screen)
        self.robot.draw(screen)
    
    def get_sensor_data(self):
        robot_pos = self.robot.get_position()
        min_distance = float('inf')
        
        for car in self.cars:
            dx = car.x - robot_pos[0]
            dy = car.y - robot_pos[1]
            distance = math.sqrt(dx*dx + dy*dy)
            min_distance = min(min_distance, distance)
        
        for ped in self.pedestrians:
            dx = ped.x - robot_pos[0]
            dy = ped.y - robot_pos[1]
            distance = math.sqrt(dx*dx + dy*dy)
            min_distance = min(min_distance, distance)
        
        for obs in self.obstacles:
            obs_center_x = obs.x + obs.width / 2
            obs_center_y = obs.y + obs.height / 2
            dx = obs_center_x - robot_pos[0]
            dy = obs_center_y - robot_pos[1]
            distance = math.sqrt(dx*dx + dy*dy)
            min_distance = min(min_distance, distance)
        
        pedestrian_data = [(p.x, p.y, p.vx, p.vy) for p in self.pedestrians]
        car_data = [(c.x, c.y, *c.get_velocity()) for c in self.cars]
        dest_pos = self.destination.get_position()
        dx = dest_pos[0] - robot_pos[0]
        dy = dest_pos[1] - robot_pos[1]
        dist_to_dest = math.sqrt(dx*dx + dy*dy)
        
        return {
            'distance_to_obstacle': min_distance,
            'pedestrians': pedestrian_data,
            'cars': car_data,
            'robot_position': robot_pos,
            'robot_heading': self.robot.heading,
            'destination': dest_pos,
            'distance_to_destination': dist_to_dest
        }


class Simulator:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption("Autonomous Delivery Robot")
        self.clock = pygame.time.Clock()
        self.environment = Environment(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        self.brain = GeminiNavigator()
        self.running = True
        self.frame = 0
        self.font = pygame.font.Font(None, 24)
        
    def run(self):
        print("Autonomous Delivery Robot - Gemini AI")
        print("Robot navigating to kitchen...")
        
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(config.FPS)
            self.frame += 1
        
        pygame.quit()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    self.environment = Environment(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
    
    def update(self):
        sensor_data = self.environment.get_sensor_data()
        command = self.brain.get_command(sensor_data)
        self.environment.robot.update(command)
        self.environment.update()
        
        if sensor_data['distance_to_destination'] < 30:
            print("Destination reached!")
    
    def draw(self):
        self.screen.fill((200, 220, 200))
        self.environment.draw(self.screen)
        
        robot_pos = self.environment.robot.get_position()
        dest_pos = self.environment.destination.get_position()
        pygame.draw.line(self.screen, (255, 0, 0), 
                        (int(robot_pos[0]), int(robot_pos[1])),
                        (int(dest_pos[0]), int(dest_pos[1])), 3)
        
        sensor_data = self.environment.get_sensor_data()
        dx = dest_pos[0] - robot_pos[0]
        dy = dest_pos[1] - robot_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        text = self.font.render(f"Distance: {int(distance)}px | Obstacle: {int(sensor_data['distance_to_obstacle'])}px", 
                               True, (0, 0, 0))
        self.screen.blit(text, (10, 10))
        
        pygame.display.flip()


def main():
    sim = Simulator()
    sim.run()


if __name__ == '__main__':
    main()
