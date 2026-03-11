import math
from google import genai
import config


class GeminiNavigator:
    def __init__(self):
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        self.frame = 0
        
    def get_command(self, sensor_data):
        self.frame += 1
        return self._quick_decision(sensor_data)
    
    def _analyze_traffic(self, sensor_data):
        robot_pos = sensor_data['robot_position']
        nearby_cars = 0
        
        for car in sensor_data['cars'][:5]:
            dx = car[0] - robot_pos[0]
            dy = car[1] - robot_pos[1]
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < 150:
                nearby_cars += 1
        
        return f"Traffic: {nearby_cars} cars nearby" if nearby_cars > 0 else "Traffic: clear"
    
    def _quick_decision(self, sensor_data):
        robot_pos = sensor_data['robot_position']
        destination = sensor_data['destination']
        heading = sensor_data['robot_heading']
        obstacle_dist = sensor_data['distance_to_obstacle']
        
        dx = destination[0] - robot_pos[0]
        dy = destination[1] - robot_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        target_angle = math.degrees(math.atan2(dy, dx))
        angle_diff = (target_angle - heading + 180) % 360 - 180
        
        if distance < 35:
            print("✅ DELIVERED!")
            return 'stop'
        
        if obstacle_dist < 35:
            print(f"🛑 EMERGENCY! {obstacle_dist:.0f}px - BACKING UP")
            return 'back'
        
        if obstacle_dist < 80:
            print(f"⚠️ Obstacle at {obstacle_dist:.0f}px - AVOIDING")
            return 'left' if angle_diff > 0 else 'right'
        
        if self.frame % 30 == 0:
            print(f"🚀 {distance:.0f}px | Heading: {heading:.0f}° → Target: {target_angle:.0f}° | Diff: {angle_diff:.0f}°")
        
        if abs(angle_diff) > 90:
            print(f"🔄 WRONG WAY! Turning {angle_diff:.0f}°")
            return 'left' if angle_diff > 0 else 'right'
        
        if abs(angle_diff) < 35:
            return 'forward'
        
        return 'left' if angle_diff > 0 else 'right'
