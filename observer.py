from pathlib import Path
import time
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from scanner import scan_file
import logger
from utils import isolate_file

PATHS_FILE = "Paths.txt"

# Global thread pool executor for handling file scans asynchronously
SCAN_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix="FileScanner-")

def scan_file_worker(file_path, event_type):
    """
    Worker function that runs in the thread pool to scan a file asynchronously.
    
    Args:
        file_path: Path to the file to scan
        event_type: Type of event that triggered the scan ("CREATED", "MODIFIED", or "INITIAL SCAN")
    
    Handles scanning, threat detection, isolation, and error handling gracefully.
    """
    # Only add delay for real-time events, not for initial scan
    if event_type != "INITIAL SCAN":
        time.sleep(1.0)  # Ensure file operations are complete before scanning
    
    try:
        logger.log(f"[{event_type}] Scanning file: {file_path}")
        scan_result = scan_file(file_path)
        logger.log(f"[{event_type}] Scan result: {scan_result}")
        
        if scan_result.startswith("Infected"):
            logger.log(f"[{event_type}] THREAT DETECTED!! This file needs to be isolated/logged.")
            threat_name = scan_result.split("(", 1)[1].rstrip(")")
            isolate_file(file_path, threat_name)
            logger.log(f"[{event_type}] File isolation completed: {file_path}")
        
    except FileNotFoundError:
        logger.log(f"[{event_type}] File no longer exists: {file_path}")
    except PermissionError:
        logger.log(f"[{event_type}] Permission denied scanning: {file_path}")
    except Exception as e:
        logger.log(f"[{event_type}] Error occurred during scan of {file_path}: {e}")

def initial_scan_thread(paths):
    """
    Scans all existing files in the monitored directories at startup.
    Submits tasks to the ThreadPoolExecutor for true concurrent scanning.
    """
    logger.print_info("\n[*] Starting initial directory scan...")
    submitted_tasks = 0
    
    for path in paths:
        if not os.path.exists(path):
            continue
        
        if os.path.isfile(path):
            # Single file - submit to thread pool
            SCAN_EXECUTOR.submit(scan_file_worker, path, "INITIAL SCAN")
            submitted_tasks += 1
        else:
            # Directory - scan recursively and submit each file to thread pool
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        SCAN_EXECUTOR.submit(scan_file_worker, file_path, "INITIAL SCAN")
                        submitted_tasks += 1
                    except Exception as e:
                        logger.log(f"[INITIAL SCAN] Error submitting {file_path}: {e}")
    
    logger.print_success(f"\n[INITIAL SCAN] Submitted {submitted_tasks} files to scanning queue. Results will appear as scans complete.")

class FileSecurityHandler(FileSystemEventHandler):
    """
    Non-blocking event handler for file system events.
    Submits scan tasks to a thread pool instead of scanning synchronously.
    """
    processing_files = set()

    def on_created(self, event):
        if not event.is_directory:
            self._submit_scan(event.src_path, "CREATED")

    def on_modified(self, event):
        if not event.is_directory and event.src_path not in self.processing_files:
            self._submit_scan(event.src_path, "MODIFIED")

    def _submit_scan(self, path, event_type):
        """
        Submit a file scan task to the thread pool.
        Returns immediately without blocking the event loop.
        """
        logger.log(f"\n--- FILE {event_type} DETECTED ---")
        self.processing_files.add(path)
        
        # Submit the scan task to the thread pool and add a callback to clean up
        future = SCAN_EXECUTOR.submit(scan_file_worker, path, event_type)
        future.add_done_callback(lambda f: self._cleanup_file(path, f))

    def _cleanup_file(self, path, future):
        """
        Cleanup callback executed after the scan worker completes.
        """
        try:
            # Retrieve any exceptions from the worker thread
            future.result()
        except Exception as e:
            logger.log(f"[CLEANUP] Unexpected error in scan worker: {e}")
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

def start_engine_with_scan():
    """
    Starts the monitoring engine and performs an initial directory scan.
    Runs both operations: file monitoring (main thread) and initial scan (separate thread).
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    paths_file = os.path.join(base_dir, PATHS_FILE)
    
    targets = []
    if os.path.exists(paths_file):
        with open(paths_file, "r") as f:
            targets = [line.strip() for line in f if line.strip()]
    
    event_handler = FileSecurityHandler() 
    observer = Observer()

    for path in targets:
        if os.path.exists(path):
            observer.schedule(event_handler, path, recursive=False)
            logger.print_info(f"   -> Watching: {path}")
        else:
            logger.print_warning(f"   [!] Invalid path skipped: {path}")

    # Start the observer FIRST to ensure it's ready before initial scan
    observer.start()
    logger.print_success("\n[SUCCESS] Engine Running. Press Ctrl+C to stop.")
    
    # Give the observer a moment to fully stabilize before starting the initial scan
    time.sleep(0.5)
    
    # Start the initial scan in a separate thread AFTER observer is running
    scan_thread = threading.Thread(target=initial_scan_thread, args=(targets,), daemon=False)
    scan_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.print_info("\n[STOP] Engine stopped.")
    
    observer.join()
    scan_thread.join()  # Wait for the scan thread to finish

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