"""
GridShield AI - MQTT Handler
WHY: Implements IoT communication pattern using MQTT protocol.
WHAT: Publishes sensor data and events; subscribes to control topics.
HOW: Uses paho-mqtt client with structured JSON payloads.
"""

import json
import threading
import time
from datetime import datetime
from typing import Dict, List, Callable, Optional
from loguru import logger

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    logger.warning("paho-mqtt not available, MQTT functionality disabled")


class MQTTHandler:
    """MQTT client for IoT sensor data publication and event streaming."""

    def __init__(self, broker_host: str = "localhost",
                 broker_port: int = 1883,
                 client_id: str = "gridshield_backend"):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client_id = client_id
        self.client = None
        self.is_connected = False
        self._message_callbacks: Dict[str, List[Callable]] = {}
        self._fallback_mode = not MQTT_AVAILABLE

        if MQTT_AVAILABLE:
            self.client = mqtt.Client(client_id=client_id)
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message

    def connect(self) -> bool:
        """Connect to MQTT broker."""
        if self._fallback_mode:
            logger.info("MQTT in fallback mode (no broker)")
            self.is_connected = True
            return True

        try:
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
            time.sleep(1)
            return self.is_connected
        except Exception as e:
            logger.warning(f"MQTT connection failed: {e}, switching to fallback mode")
            self._fallback_mode = True
            self.is_connected = True
            return True

    def disconnect(self):
        if self.client and not self._fallback_mode:
            self.client.loop_stop()
            self.client.disconnect()
        self.is_connected = False

    def publish_sensor_data(self, sensor_id: str, data: Dict):
        """Publish sensor reading to MQTT."""
        topic = f"grid/sensors/{sensor_id}/data"
        payload = json.dumps(data, default=str)

        if self._fallback_mode:
            # In fallback mode, just invoke callbacks
            for cb in self._message_callbacks.get(topic, []):
                cb(topic, data)
            return True

        try:
            result = self.client.publish(topic, payload, qos=1)
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            logger.error(f"MQTT publish error: {e}")
            return False

    def publish_event(self, event_type: str, data: Dict):
        """Publish system event."""
        topic = f"grid/{event_type}"
        payload = json.dumps(data, default=str)

        if self._fallback_mode:
            for cb in self._message_callbacks.get(topic, []):
                cb(topic, data)
            return True

        try:
            self.client.publish(topic, payload, qos=1)
            return True
        except:
            return False

    def publish_batch(self, readings: List[Dict]):
        """Publish batch of sensor readings."""
        for reading in readings:
            sensor_id = reading.get("sensor_id", "unknown")
            self.publish_sensor_data(sensor_id, reading)

    def subscribe(self, topic: str, callback: Callable):
        """Subscribe to a topic with callback."""
        if topic not in self._message_callbacks:
            self._message_callbacks[topic] = []
        self._message_callbacks[topic].append(callback)

        if not self._fallback_mode and self.client:
            self.client.subscribe(topic, qos=1)

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.is_connected = True
            logger.info("Connected to MQTT broker")
            # Resubscribe
            for topic in self._message_callbacks:
                client.subscribe(topic, qos=1)
        else:
            logger.error(f"MQTT connection failed with code {rc}")

    def _on_disconnect(self, client, userdata, rc):
        self.is_connected = False
        if rc != 0:
            logger.warning("Unexpected MQTT disconnection")

    def _on_message(self, client, userdata, msg):
        topic = msg.topic
        try:
            data = json.loads(msg.payload.decode())
        except:
            data = {"raw": msg.payload.decode()}

        for pattern, callbacks in self._message_callbacks.items():
            if mqtt.topic_matches_sub(pattern, topic):
                for cb in callbacks:
                    try:
                        cb(topic, data)
                    except Exception as e:
                        logger.error(f"MQTT callback error: {e}")


# Global MQTT handler
mqtt_handler = MQTTHandler()
