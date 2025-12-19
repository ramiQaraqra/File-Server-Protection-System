from pathlib import Path
import time
import os
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from scanner import scan_file
import logger
from utils import isolate_file

PATHS_FILE = "Paths.txt"
class FileSecurityHandler(FileSystemEventHandler):
    processing_files = set()

    def on_created(self, event):
        if not event.is_directory:
            self.process(event.src_path, "CREATED")

    def on_modified(self, event):
        if not event.is_directory and event.src_path not in self.processing_files:
             self.process(event.src_path, "MODIFIED")

    def process(self, path, event_type):
        time.sleep(1.0)  # Ensure file operations are complete
        if path in self.processing_files:
            logger.log(f"[{event_type}] Ignored: File {os.path.basename(path)} is already being processed.")
            return

        logger.log(f"\n--- FILE {event_type} DETECTED ---")
        self.processing_files.add(path)
        
        try:
            logger.log(f"Scanning file: {path}")
            scan_result = scan_file(path)
            logger.log(f"Scan result: {scan_result}")
            
            if scan_result.startswith("Infected"):
                logger.log("THREAT DETECTED!! This file needs to be isolated/logged.")
                threat_name = scan_result.split("(", 1)[1].rstrip(")")  
                isolate_file(path, threat_name)
                            
        except Exception as e:
            logger.log(f"An error occurred during scan process: {e}")
        
        finally:
            self.processing_files.discard(path)

def start_engine():
    """
    Main entry point for the CLI
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    paths_file = os.path.join(base_dir, PATHS_FILE)
    
    targets = []
    if os.path.exists(paths_file):
        with open(paths_file, "r") as f:
            targets = [line.strip() for line in f if line.strip()]
    
    #if not targets:
    #    DECIDE("[WARNING] No directories found. Use 'add' command first.")
    
    event_handler = FileSecurityHandler() 
    observer = Observer()

    for path in targets:
        if os.path.exists(path):
            observer.schedule(event_handler, path, recursive=False)
            logger.print_info(f"   -> Watching: {path}")
        else:
            logger.print_warning(f"   [!] Invalid path skipped: {path}")

    try:
        observer.start()
        logger.print_success("\n[SUCCESS] Engine Running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.print_info("\n[STOP] Engine stopped.")
    
    observer.join()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        new_path = sys.argv[1].strip()
        with open(PATHS_FILE, 'a') as f:
            f.write(f"\n{new_path}")
        logger.log_and_print(f"Added new path: {new_path}")

    event_handler = FileSecurityHandler()
    observer = Observer()
    if not os.path.exists(PATHS_FILE):
        open(PATHS_FILE, 'w').close()

    with open(PATHS_FILE, 'r') as paths_file:
        for path in paths_file:
            path = path.strip()
            if not path:
                continue
            if not os.path.isdir(path):
                logger.log(f" [NEW] Creating directory: {path}")
                try:
                    os.makedirs(path, exist_ok=True)
                except OSError as e:
                    logger.log(f" [ERR] Could not create {path}: {e}")
                    continue

            observer.schedule(event_handler, path, recursive=True)
            logger.log(f" [OK] Monitoring: {path}")

    observer.start()
    #DECIDE(f"\nSTARTING MONITORING... Drop or Modify files to test.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()