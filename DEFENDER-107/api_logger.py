# api_logger.py
# Singleton logger for sending game events and scores to remote API
import requests
import threading
import queue
import time
from settings import API_URL


# --- PATTERN: SINGLETON ---
# Ensures only one APILogger instance exists.
# All game events are routed through this single logging gateway.
class APILogger:
    _instance = None
    _url = API_URL
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
        batch = []
        last_flush = time.time()
        
        while True:
            try:
                task = self._queue.get(timeout=1)
                if task is None: break
                
                method, url, payload, headers, priority = task
                
                # Priority 2 = Immediate (Scores)
                if priority >= 2:
                    if batch:
                        self._flush_batch(batch)
                        batch = []
                    try:
                        requests.post(url, json=payload, headers=headers, timeout=5)
                    except: pass
                else:
                    # Generic logs are batched
                    batch.append(payload)
                
                # Check flush conditions
                if len(batch) >= 10 or (time.time() - last_flush > 5 and batch):
                    self._flush_batch(batch)
                    batch = []
                    last_flush = time.time()
                
                self._queue.task_done()
            except queue.Empty:
                if batch and time.time() - last_flush > 5:
                    self._flush_batch(batch)
                    batch = []
                    last_flush = time.time()
                continue
            except Exception as e:
                time.sleep(1)

    def _flush_batch(self, batch):
        try:
            batch_url = self._url + "/batch"
            headers = {"X-API-KEY": self._api_key}
            requests.post(batch_url, json=batch, headers=headers, timeout=5)
        except: pass

    def log(self, level, message):
        headers = {"X-API-KEY": self._api_key}
        payload = {"level": level, "message": message}
        # Priority 1 for normal logs (batched)
        self._queue.put(('POST', self._url, payload, headers, 1))

    def submit_score(self, username, score):
        headers = {"X-API-KEY": self._api_key}
        payload = {"username": username, "score": score}
        score_url = self._url.replace("/log", "/score")
        # Priority 2 for scores (immediate)
        self._queue.put(('POST', score_url, payload, headers, 2))

    def shutdown(self):
        self._queue.put(None)
        if self._worker_thread:
            self._worker_thread.join(timeout=2) # Wait up to 2 seconds for worker to finish
