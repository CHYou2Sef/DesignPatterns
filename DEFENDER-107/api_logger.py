# api_logger.py
import requests
import threading
import queue
import time

# --- PATTERN: SINGLETON ---
# Ensures only one APILogger instance exists.
# All game events are routed through this single logging gateway.
class APILogger:
    _instance = None
    _url = "https://designpatterns.onrender.com/log"
    _api_key = "Defender-gamo-pwd-2025" 
    _queue = queue.Queue()
    _worker_thread = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(APILogger, cls).__new__(cls)
            cls._instance._start_worker()
        return cls._instance

    def _start_worker(self):
        if self._worker_thread is None:
            self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self._worker_thread.start()

    def _worker_loop(self):
        while True:
            try:
                task = self._queue.get(timeout=1)
                if task is None: break
                method, url, payload, headers, timeout = task
                requests.post(url, json=payload, headers=headers, timeout=timeout)
                self._queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Logger worker error: {e}")
                time.sleep(1)

    def log(self, level, message):
        headers = {"X-API-KEY": self._api_key}
        payload = {"level": level, "message": message}
        self._queue.put(('POST', self._url, payload, headers, 1))

    def submit_score(self, username, score):
        headers = {"X-API-KEY": self._api_key}
        payload = {"username": username, "score": score}
        score_url = self._url.replace("/log", "/score")
        self._queue.put(('POST', score_url, payload, headers, 2))

    def shutdown(self):
        self._queue.put(None)
