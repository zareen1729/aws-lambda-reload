#!/usr/bin/env python3
import os, sys, time, yaml, threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from lambda_update import update_lambda_for_function
from logs_streamer import stream_logs_for_function

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.yaml')

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, fn_cfg):
        super().__init__()
        self.fn_cfg = fn_cfg
        self.debounce = 1.0
        self._last = 0

    def on_any_event(self, event):
        if event.is_directory:
            return
        now = time.time()
        if now - self._last < self.debounce:
            return
        self._last = now
        path = event.src_path
        if path.endswith(('.py', '.js', '.go', '.zip')):
            print(f"[watcher] Detected change: {path}")
            threading.Thread(target=self._deploy_and_stream).start()

    def _deploy_and_stream(self):
        try:
            update_lambda_for_function(self.fn_cfg)
            stream_logs_for_function(self.fn_cfg)
        except Exception as e:
            print(f"[watcher] Error: {e}")

def load_config(path=CONFIG_PATH):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def main():
    if not os.path.exists(CONFIG_PATH):
        print(f"Config not found at {CONFIG_PATH}")
        sys.exit(1)
    cfg = load_config()
    functions = cfg.get('functions', [])
    if not functions:
        print("No functions configured in config.yaml")
        sys.exit(1)

    observer = Observer()
    for fn in functions:
        watch_path = os.path.abspath(fn.get('path'))
        os.makedirs(watch_path, exist_ok=True)
        handler = ChangeHandler(fn)
        observer.schedule(handler, path=watch_path, recursive=True)
        print(f"[watcher] Watching {watch_path} for function {fn.get('name')}")

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    main()
