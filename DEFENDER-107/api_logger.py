# api_logger.py
import requests
import threading

# --- PATTERN: SINGLETON ---
# Ensures only one APILogger instance exists.
# All game events are routed through this single logging gateway.
class APILogger:
    _instance = None
    _url = "https://designpatterns.onrender.com/log"
    _api_key = "Defender-gamo-pwd-2025" 

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(APILogger, cls).__new__(cls)
        return cls._instance

    def log(self, level, message):
        def send():
            try:
                headers = {"X-API-KEY": self._api_key}
                payload = {"level": level, "message": message}
                # Short timeout (1s) so game doesn't hang if server is slow
                requests.post(self._url, json=payload, headers=headers, timeout=1)
            except Exception as e:
                # Silently fail in production, or maybe print to console in dev
                print(f"Log failed: {e}")
        
        # Daemon thread ensures log attempts don't stop the game from closing
        threading.Thread(target=send, daemon=True).start()

    def submit_score(self, username, score):
        def send():
            try:
                headers = {"X-API-KEY": self._api_key}
                payload = {"username": username, "score": score}
                # Use base URL logic to replace /log with /score
                score_url = self._url.replace("/log", "/score")
                requests.post(score_url, json=payload, headers=headers, timeout=2)
            except Exception as e:
                print(f"Score submission failed: {e}")
        
        threading.Thread(target=send, daemon=True).start()