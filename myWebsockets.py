from loguru import logger
import json
import asyncio
from routers.middlewares import validateToken
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os

load_dotenv()

class WebsocketsConfig:
    def __init__(self, app):
        self.app = app
        self.queue = asyncio.Queue()  # Cola para pasar mensajes de MQTT a WebSocket
        self.init_mqtt_client()

        @app.websocket("/")
        async def websocketsHandler(request, ws):
            token = "hola"  # request.cookies.get("authToken")
            if not token:
                await ws.close(code=1008, reason="Missing authentication token")
                return
            
            logger.info("New connection to WebSocket")

            # Tarea asincrónica para enviar mensajes MQTT al cliente WebSocket
            send_task = asyncio.create_task(self.send_mqtt_to_ws(ws))

            try:
                while True:
                    data = await ws.recv()
                    if data:
                        try:
                            parsed_data = _MessageData.parse(data)
                        except json.JSONDecodeError:
                            logger.error("Failed to parse JSON data")
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
            finally:
                send_task.cancel()  # Cancelar la tarea cuando el cliente se desconecta

    def init_mqtt_client(self):
        """Inicializa el cliente MQTT y lo configura para manejar eventos."""
        broker = os.getenv("MQTT_BROKER")  # Cambia al broker que estés usando
        port = int(os.getenv("MQTT_PORT"))
        topic_distancia = "sensor/distancia"
        topic_toque = "sensor/toque"
        topic_test = "message/event"

        self.mqtt_client = mqtt.Client()

        # Configura los callbacks de MQTT
        def on_connect(client, userdata, flags, rc):
            logger.info("Conectado al broker MQTT")
            client.subscribe(topic_distancia)
            client.subscribe(topic_toque)
            client.subscribe(topic_test)

        async def on_message(client, userdata, msg):
            try:
                message = json.loads(msg.payload.decode())
                message = _MqttMessageData(message)
                topic = msg.topic
                message.setMqttTopic(topic)
                logger.info(f"Mensaje MQTT recibido: {message.value} en el topic {topic}")
                await self.queue.put(message)  # Evita asyncio.run
            except json.JSONDecodeError:
                logger.error(f"Mensaje no es un JSON válido: {msg.payload.decode()}")
            except Exception as e:
                logger.error(f"Error en on_message: {e}")

        self.mqtt_client.on_message = lambda c, u, m: asyncio.create_task(on_message(c, u, m))

    async def send_mqtt_to_ws(self, ws):
        """Envía mensajes de la cola MQTT a WebSocket."""
        while True:
            try:
                message: _MqttMessageData = await self.queue.get()
                if not message.hasValues():
                    await ws.send(json.dumps({"message": "bad reading from sensors, or data was malformed"}))
                    continue
                await ws.send(json.dumps({"event": message.topic, "data": message.value, "message": "message from sensors"}))
            except Exception as e:
                logger.error(f"Error enviando mensaje al WebSocket: {e}")
                break  # Sal del bucle si el cliente WebSocket se desconecta


class _MessageData:
    def __init__(self, rawData: dict):
        self.type: str = rawData.get('type')
        self.event: str = rawData.get('event')
        self.value : int | any = rawData.get('value')
        self.body: dict = rawData.get('body')

    def _checkToken(token: str = None):
        if token is None:
            raise ValueError("error, token doesn't exist")

    @staticmethod
    def parse(stringRawData: str):
        rawData = json.loads(stringRawData)
        return _MessageData(rawData)

class _MqttMessageData:
    def __init__(self, rawData: dict):
        self.event : str = rawData.get("event")
        self.value : any = rawData.get("value")
        self.topic : str = None
        
    def setMqttTopic(self, topic):
        self.topic = topic
        
    def hasValues(self):
        return all([self.event, self.value, self.topic])
