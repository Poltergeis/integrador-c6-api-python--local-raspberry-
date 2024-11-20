import os
from loguru import logger
from dotenv import load_dotenv
from tortoise import Tortoise

load_dotenv()

def connectToDatabase(app):
    try:
        @app.listener("before_server_start")
        async def init_orm(app, loop):
            db_user = os.getenv("DB_USER", "root")
            db_password = os.getenv("DB_PASSWORD", "")
            db_host = os.getenv("DB_HOST", "localhost")
            db_name = os.getenv("DB_NAME", "vitalGuard")

            db_url = f"mysql://{db_user}:{db_password}@{db_host}/{db_name}"

            await Tortoise.init(
                db_url=db_url,
                modules={"models": ["models.models"]}
            )
            await Tortoise.generate_schemas()
            logger.info("Conexión a la base de datos establecida.")

        @app.listener("after_server_stop")
        async def close_orm(app, loop):
            await Tortoise.close_connections()
            logger.info("Conexión a la base de datos cerrada.")
    
    except Exception as e:
        logger.error(f"La conexión a la base de datos falló.\n{e}")
        return None
