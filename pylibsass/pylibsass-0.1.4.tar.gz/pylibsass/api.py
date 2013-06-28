from .events import FileSystemEvents

from watchdog.observers import Observer

def watch(source_path, dest_path):
    """Watches for filesystem changes and compiles SCSS to CSS

    This is an async function.

    :param str source_path: The source directory to watch. All .scss files are
                            monitored.
    :param str dest_path: The destination directory where the resulting CSS
                          files should go. The filename will be identical to
                          the original, except the extension will be `.css`.

    """
    # Setup Watchdog
    handler = FileSystemEvents(source_path, dest_path)

    # Always run initial compile
    handler.compile_scss()

    observer = Observer(timeout=5000)
    observer.schedule(handler, path=source_path, recursive=True)
    observer.start()

