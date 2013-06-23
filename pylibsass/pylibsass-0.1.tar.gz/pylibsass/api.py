from .events import FileSystemEvents

from watchdog.observers import Observer

def watch(source_path, dest_path):
    # Setup Watchdog
    handler = FileSystemEvents(source_path, dest_path)

    # Always run initial compile
    handler.compile_scss()

    observer = Observer(timeout=5000)
    observer.schedule(handler, path=source_path, recursive=True)
    observer.start()

