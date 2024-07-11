import subprocess
import threading
import time
from collections import deque


class RPLidarProcess:
    def __init__(self):
        self.process = None
        self.output_queue = deque(maxlen=500)
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

    def get_latest_output(self, num_lines=1000):
        with self.lock:
            return list(self.output_queue)[-num_lines:]

    def stop_process(self):
        self.stop_event.set()
        if self.process:
            self.process.terminate()
            self.process.wait()


if __name__ == "__main__":

    bg_process = RPLidarProcess()

    try:
        while True:
            time.sleep(10)  # Adjust the sleep time as needed
            latest_output = bg_process.get_latest_output()
            print("\n".join(latest_output))
    except KeyboardInterrupt:
        bg_process.stop_process()
        print("Process terminated.")

