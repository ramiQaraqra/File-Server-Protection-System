from pathlib import Path
import time
import os
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from scanner import scan_file


class FileSecurityHandler(FileSystemEventHandler):
    processing_files = set()

    def on_created(self, event):
        if not event.is_directory:
            self.process(event.src_path, "CREATED")

    def on_modified(self, event):
        if not event.is_directory and event.src_path not in self.processing_files:
             self.process(event.src_path, "MODIFIED")

    def process(self, path, event_type):
        if path in self.processing_files:
            print(f"[{event_type}] Ignored: File {os.path.basename(path)} is already being processed.")
            return

        print(f"\n--- FILE {event_type} DETECTED ---")
        self.processing_files.add(path)
        
        try:
            print(f"Scanning file: {path}")
            scan_result = scan_file(path)
            print(f"Scan result: {scan_result}")
            
            if scan_result.startswith("Infected"):
                #isolate the file if it was infected
                print("THREAT DETECTED!! This file needs to be isolated/logged.")
            
        except Exception as e:
            print(f"An error occurred during scan process: {e}")
        
        finally:
            self.processing_files.discard(path)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        new_path = sys.argv[1].strip()
        with open('paths.txt', 'a') as f:
            f.write(f"\n{new_path}")
        print(f"Added new path: {new_path}")

    event_handler = FileSecurityHandler()
    observer = Observer()
    if not os.path.exists('paths.txt'):
        open('paths.txt', 'w').close()

    with open('paths.txt', 'r') as paths_file:
        for path in paths_file:
            path = path.strip()
            if not path:
                continue
            if not os.path.isdir(path):
                print(f" [NEW] Creating directory: {path}")
                try:
                    os.makedirs(path, exist_ok=True)
                except OSError as e:
                    print(f" [ERR] Could not create {path}: {e}")
                    continue

            observer.schedule(event_handler, path, recursive=True)
            print(f" [OK] Monitoring: {path}")

    observer.start()
    print(f"\nSTARTING MONITORING... Drop or Modify files to test.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()