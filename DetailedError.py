from loguru import logger

class DetailedError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        
        details = ", ".join(f"{key} = {value}" for key, value in kwargs.items())
        
        logger.error(f"Error details: {details}")