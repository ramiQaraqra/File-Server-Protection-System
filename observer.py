from pathlib import Path
import time
import sys
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from scanner import scan_file

OBSERVED_FOLDER = "C:\Users\rami6\OneDrive\Desktop\miniproject\To_Observe"
ISOLATION_FOLDER = ""

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
            print(f"Scanning file: {os.path.basename(path)}...")
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
    if not os.path.isdir(OBSERVED_FOLDER):
        print(f"Creating monitoring directory: {OBSERVED_FOLDER}")
        os.makedirs(OBSERVED_FOLDER)
        
    for file in Path(OBSERVED_FOLDER).rglob('*.*'):
        scan_result = scan_file(file)
        #isolate the file if it was infected
    event_handler = FileSecurityHandler()
    observer = Observer()
    observer.schedule(event_handler, OBSERVED_FOLDER, recursive=True)
    observer.start()
    
    print(f"\nSTARTING MONITORING...")
    print(f"Monitoring directory: {OBSERVED_FOLDER}. Drop files here.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()