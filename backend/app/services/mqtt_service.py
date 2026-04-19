import paho.mqtt.client as mqtt
import json
import os
from typing import Callable, Optional
import asyncio
from datetime import datetime

class MQTTService:
    def __init__(self):
        self.broker_host = os.getenv("MQTT_BROKER_HOST", "localhost")
        self.broker_port = int(os.getenv("MQTT_BROKER_PORT", "1883"))
        self.username = os.getenv("MQTT_USERNAME", "")
        self.password = os.getenv("MQTT_PASSWORD", "")
        
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        
        self.callbacks: dict = {}
        self.is_connected = False
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("MQTT Connected successfully")
            self.is_connected = True
            # Subscribe to all drone telemetry topics
            client.subscribe("drones/+/telemetry")
            client.subscribe("drones/+/status")
        else:
            print(f"MQTT Connection failed with code {rc}")
    
    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = json.loads(msg.payload.decode())
        
        # Handle telemetry updates
        if "/telemetry" in topic:
            drone_id = topic.split("/")[1]
            self.handle_telemetry(drone_id, payload)
        
        # Handle status updates
        elif "/status" in topic:
            drone_id = topic.split("/")[1]
            self.handle_status(drone_id, payload)
    
    def handle_telemetry(self, drone_id: str, data: dict):
        """Handle incoming telemetry data"""
        if "telemetry" in self.callbacks:
            for callback in self.callbacks["telemetry"]:
                callback(drone_id, data)
    
    def handle_status(self, drone_id: str, data: dict):
        """Handle status updates"""
        if "status" in self.callbacks:
            for callback in self.callbacks["status"]:
                callback(drone_id, data)
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"MQTT connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.client.loop_stop()
        self.client.disconnect()
    
    def subscribe_telemetry(self, callback: Callable):
        """Subscribe to telemetry updates"""
        if "telemetry" not in self.callbacks:
            self.callbacks["telemetry"] = []
        self.callbacks["telemetry"].append(callback)
    
    def subscribe_status(self, callback: Callable):
        """Subscribe to status updates"""
        if "status" not in self.callbacks:
            self.callbacks["status"] = []
        self.callbacks["status"].append(callback)
    
    def publish_command(self, drone_id: str, command: str, payload: dict):
        """Publish a command to a drone"""
        topic = f"drones/{drone_id}/commands"
        message = {
            "command": command,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.client.publish(topic, json.dumps(message))
        return True
    
    def publish_mission_plan(self, drone_id: str, mission: dict):
        """Publish mission plan to drone"""
        topic = f"drones/{drone_id}/mission"
        self.client.publish(topic, json.dumps(mission))
        return True

# Global MQTT service instance
mqtt_service = MQTTService()
