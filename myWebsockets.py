from gmqtt import Client as MQTTClient
from loguru import logger
import asyncio
import json

class WebsocketsConfig:
    def __init__(self, app, mqtt_config):
        """
        Inicializa el manejador de WebSockets y MQTT.
        :param app: Instancia de la aplicación Sanic.
        :param mqtt_config: Diccionario con configuración del broker MQTT.
        """
        self.app = app
        self.queue = asyncio.Queue()  # Cola para pasar mensajes de MQTT a WebSocket
        self.mqtt_config = mqtt_config
        self.mqtt_client = None

        # Configurar WebSocket
        self.register_websocket_route()
        
        # Iniciar el cliente MQTT dentro del bucle de eventos
        app.add_task(self.init_mqtt_client())

    def register_websocket_route(self):
        """Registra la ruta de WebSocket en Sanic."""
        @self.app.websocket("/ws")
        async def websockets_handler(request, ws):
            token = True  # Aquí podrías usar validateToken o cookies reales
            if not token:
                await ws.close(code=1008, reason="Missing authentication token")
                return
            
            logger.info("Nueva conexión WebSocket")
            send_task = asyncio.create_task(self.send_mqtt_to_ws(ws))

            try:
                while True:
                    data = await ws.recv()
                    if data:
                        logger.info(f"Mensaje recibido del WebSocket: {data}")
                        await self.handle_ws_message(data)
            except Exception as e:
                logger.error(f"Error en WebSocket: {e}")
            finally:
                send_task.cancel()
                logger.info("Conexión WebSocket cerrada")

    async def handle_ws_message(self, message):
        """
        Procesa mensajes recibidos desde WebSocket.
        """
        try:
            parsed_data = _MessageData.parse(message)
            logger.info(f"Mensaje procesado del WebSocket: {parsed_data.__dict__}")
            # Aquí puedes agregar lógica para reenviar al broker MQTT, si es necesario.
        except json.JSONDecodeError:
            logger.error("Mensaje no es un JSON válido.")

    async def send_mqtt_to_ws(self, ws):
        """
        Envía mensajes de MQTT a WebSocket.
        """
        while True:
            try:
                message = await self.queue.get()
                await ws.send(json.dumps(message))
            except Exception as e:
                logger.error(f"Error enviando mensaje al WebSocket: {e}")
                break

    async def init_mqtt_client(self):
        """
        Inicializa y configura el cliente MQTT.
        """
        self.mqtt_client = MQTTClient("sanic_client")

        @self.mqtt_client.on_connect
        def on_connect(client, flags, rc, properties):
            logger.info("Conectado al broker MQTT")
            topics = [self.mqtt_config.get("topic_distancia"), 
                      self.mqtt_config.get("topic_toque"), 
                      self.mqtt_config.get("topic_temperatura"),
                      self.mqtt_config.get("topic_bpm"),
                      "message/event"]
            for topic in topics:
                if topic:
                    self.mqtt_client.subscribe(topic, qos=1)

        @self.mqtt_client.on_message
        async def on_message(client, topic, payload, qos, properties):
            logger.info(f"Mensaje recibido del MQTT: {payload.decode()} en el tópico {topic}")
            try:
                message = {
                    "topic": topic,
                    "payload": json.loads(payload.decode()),
                }
                await self.queue.put(message)
            except json.JSONDecodeError:
                logger.error("Mensaje MQTT no es un JSON válido.")

        self.mqtt_client.on_disconnect = lambda client, packet, exc: logger.warning("Desconectado del broker MQTT")
        self.mqtt_client.on_subscribe = lambda client, mid, qos: logger.info(f"Suscrito al tópico con QoS: {qos}")

        broker = self.mqtt_config.get("broker", "localhost")
        port = self.mqtt_config.get("port", 1883)
        username = self.mqtt_config.get("username")
        password = self.mqtt_config.get("password")

        if username and password:
            self.mqtt_client.set_auth_credentials(username, password)

        await self.mqtt_client.connect(broker, port)

        # Ejecutar el bucle de eventos del cliente MQTT en el bucle principal de asyncio
        while True:
            await asyncio.sleep(1)

class _MessageData:
    def __init__(self, rawData: dict):
        self.event: str = rawData.get('Event')
        self.value: int | any = rawData.get('valor')

    @staticmethod
    def parse(stringRawData: str):
        rawData = json.loads(stringRawData)
        return _MessageData(rawData)
