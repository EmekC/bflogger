import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def get_default_path():
    local_appdata = os.getenv("LOCALAPPDATA")
    if not local_appdata:
        return None
    return os.path.join(local_appdata, "Temp", "Battlefieldâ„¢ 6", "PortalLog.txt")

def sanitize_path(path):
    # Remove quotes pasted from Explorer
    return path.strip().strip('"').strip("'")

class LogTailHandler(FileSystemEventHandler):
    def __init__(self, file_to_watch):
        super().__init__()
        self.file_to_watch = os.path.abspath(file_to_watch)
        self.last_size = os.path.getsize(file_to_watch) if os.path.exists(file_to_watch) else 0

    def read_new_lines(self):
        """Read only new lines since last modification"""
        if not os.path.exists(self.file_to_watch):
            return
        current_size = os.path.getsize(self.file_to_watch)
        if current_size < self.last_size:
            # File was truncated or rewritten
            self.last_size = 0
        with open(self.file_to_watch, "r", encoding="utf-8", errors="replace") as f:
            f.seek(self.last_size)
            new_content = f.read()
            if new_content.strip():
                print(new_content.strip())
        self.last_size = current_size

    def on_modified(self, event):
        if os.path.abspath(event.src_path) == self.file_to_watch:
            self.read_new_lines()

    def on_created(self, event):
        if os.path.abspath(event.src_path) == self.file_to_watch:
            print(f"\n[{time.strftime('%H:%M:%S')}] Log file recreated, resuming...\n")
            self.last_size = 0
            self.read_new_lines()

if __name__ == "__main__":
    default_path = get_default_path()
    if default_path and os.path.exists(default_path):
        file_to_watch = default_path
    else:
        print("❌ Could not find PortalLog.txt automatically.")
        file_to_watch = input("Please enter the full path to PortalLog.txt: ").strip()
        file_to_watch = sanitize_path(file_to_watch)
        while not os.path.exists(file_to_watch):
            print("⚠️ Path not found. Try again (quotes will be ignored automatically).")
            file_to_watch = sanitize_path(input("Path: ").strip())

    watch_dir = os.path.dirname(file_to_watch)
    print(f"✅ Watching and tailing log file:\n{file_to_watch}\n")

    event_handler = LogTailHandler(file_to_watch)
    observer = Observer()
    observer.schedule(event_handler, watch_dir, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
