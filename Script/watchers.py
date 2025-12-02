# watchers.py
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigWatcher:
    def __init__(self, parent):
        self.parent = parent
        self.config_dir = os.path.join(os.path.dirname(__file__), "..", "Config")
        self.observer = None
        self._start()

    def _start(self):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

        event_handler = _ConfigEventHandler(self.parent.update_config)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.config_dir, recursive=True)
        self.observer.start()
        
    def stop(self):
        # Stops the watchdog observer thread cleanly
        if self.observer:
            self.observer.stop()
            self.observer.join()

class _ConfigEventHandler(FileSystemEventHandler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def on_any_event(self, event):
        if not event.is_directory:
            self.callback()