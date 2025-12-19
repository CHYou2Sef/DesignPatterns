# api_logger.py
import requests
import threading

class APILogger:
    _instance = None
    _url = "http://127.0.0.1:5000/log"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(APILogger, cls).__new__(cls)
        return cls._instance

    def log(self, level, message):
        def send():
            try:
                requests.post(self._url, json={"level": level, "message": message}, timeout=1)
            except:
                pass # Fail silently in game to prevent lag
        
        threading.Thread(target=send, daemon=True).start()