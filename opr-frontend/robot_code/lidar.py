import subprocess
import threading
import time
from collections import deque
from math import floor


class RPLidarProcess:
    def __init__(self):
        self.process = None
        self.output_queue = deque(maxlen=8000)
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.executable = "/home/pi/opr-frontend/opr-frontend/robot_code/rplidar.sh"

        self.start_process()

    def start_process(self):
        self.process = subprocess.Popen(
            [self.executable],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        threading.Thread(target=self._enqueue_output, daemon=True).start()

    def _enqueue_output(self):
        for line in iter(self.process.stdout.readline, ''):
            if self.stop_event.is_set():
                break
            with self.lock:
                self.output_queue.append(line.strip())
        self.process.stdout.close()

    def get_latest_output(self, num_lines=8000):
        with self.lock:
            return list(self.output_queue)[-num_lines:]

    def stop_process(self):
        self.stop_event.set()
        if self.process:
            self.process.terminate()
            self.process.wait()




