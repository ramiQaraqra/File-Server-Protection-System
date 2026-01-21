# Project Documentation

**Project name:** CQr (Secure)
**Developers:** Mohamed Ali, Rami Qaraqra

## Tool Overview & Goal Fulfillment
**What the tool does:**
CQr is a real-time file server protection system designed to secure Windows environments. It continuously monitors designated directories for file system events. When such events occur, CQr instantly scans the file using the local ClamAV engine. If it finds a file infected, it efficiently neutralizes the threat by an automated response: locks the file and moves it to a restricted quarantine folder.

**Does it answer the goal?**
Yes. The primary goal was to prevent malware on a server. CQr achieves this by:
1. **Detection:** Catching viruses immediately upon creation.
2. **Isolation:** Removing the file from the public protected directory before other users can "touch" it.
3. **Notification:** Replaces the infected file with a safe text note alerting the users.

## Challenges We Faced
**Quarantine Permission Lockout:**
When implementing the secure quarantine folder using Windows ACLs (`icacls`), we initially set the permissions too strictly (`/inheritance:r`), causing the script itself (running as a user) to lose write access.

* **Resolution:** We resolved this by modifying the ACL command to explicitly grant the `SYSTEM` and `Administrators` group full control while removing standard `Users`.

## Strengths and Weaknesses

### Strengths
* **Zero-Latency Monitoring:** Uses kernel-level file system events (`watchdog`) rather than slow polling intervals.
* **Non-Blocking Architecture:** Implements a ThreadPoolExecutor with 4 concurrent worker threads, enabling the observer to handle multiple large file uploads without missing smaller files created during scans.
* **Secure Quarantine:** The quarantine folder is not just a hidden folder; it is protected at the OS level (ACLs), preventing unauthorized users from accessing or restoring the malware.
* **User Experience:** Features a polished CLI (`CQr.py`) with color-coded logs and an automated setup guide for ClamAV integration.
* **Initial Scan Capability:** Supports scanning all existing files in monitored directories at startup with the `start scan` command, providing comprehensive coverage.

### Weaknesses
* **Signature Reliance:** Since it relies on ClamAV, it detects known threats (Signature-based) but may miss brand-new "Zero-Day" attacks that lack signatures.

## Description of Tool Operation (Workflow)
The system follows a pipeline architecture with both real-time and batch scanning capabilities:

### Configuration Phase
1. **Configuration:** The user adds paths to `Paths.txt` via the CLI command `python CQr.py add <path>`.

### Real-Time Monitoring Phase (Command: `python CQr.py start`)
2. **Observation:** The `observer.py` module starts the watchdog observer, listening for `FILE CREATED` or `FILE MODIFIED` events in the target folders.
3. **Non-Blocking Submission:** When an event occurs, the file path is submitted to a ThreadPoolExecutor (4 concurrent workers) instead of being scanned synchronously.
4. **Parallel Scanning:** The scanner worker thread communicates with the local ClamAV Daemon via TCP (Port 3310) to request a scan, while the observer continues monitoring for other files.
5. **Response:**
   * **If Clean:** The event is logged as safe.
   * **If Infected:** `utils.py` is triggered. It calculates a unique ID, moves the file to `C:\CQr_Quarantine`, changes the extension to `.infected`, and writes a warning note in the original location.

### Initial Scan Phase (Command: `python CQr.py start scan`)
6. **Startup Initialization:** Upon execution, the system initiates a separate thread that performs a recursive scan of all existing files in the configured directories.
7. **Parallel Operation:** The initial scan runs concurrently with real-time monitoring, allowing the system to immediately detect new files while scanning existing ones.
8. **Threat Response:** Any infected files discovered during the initial scan are isolated following the same isolation procedure as real-time detections.

## Technical Architecture & Implementation Details

### Non-Blocking Event Handler (v2.0 Update)
The refactored `FileSecurityHandler` class implements a non-blocking architecture using `concurrent.futures.ThreadPoolExecutor`:

* **Thread Pool Configuration:** A global executor with 4 concurrent worker threads handles file scan operations.
* **Asynchronous Task Submission:** Event handlers (`on_created`, `on_modified`) submit scan tasks to the pool and return immediately, preventing the observer from blocking.
* **Worker Function:** The `scan_file_worker()` function encapsulates all scanning logic, threat detection, and file isolation within a dedicated thread context.
* **Graceful Error Handling:** Worker threads catch and log specific exceptions (`FileNotFoundError`, `PermissionError`, etc.) without crashing the observer.
* **Cleanup Callbacks:** A `_cleanup_file()` callback executes after each scan completes, ensuring proper resource management and file status tracking.

### Advantage of Non-Blocking Design
The non-blocking architecture solves the critical "large file scanning" problem:
- **Before:** If a 10GB file was created, the observer would wait (block) while ClamAV scanned it, missing smaller files uploaded during that scan window.
- **After:** The observer submits the 10GB scan to a worker thread and continues monitoring. A 1MB malware file created during the large file scan is immediately queued to another worker thread, reducing response time significantly.

### CLI Commands
The system provides the following commands via `python CQr.py`:
- `python CQr.py add <path>` - Add a directory to the monitor list
- `python CQr.py list` - Display all monitored paths
- `python CQr.py start` - Launch real-time file monitoring
- `python CQr.py start scan` - Launch real-time monitoring + initial directory scan (NEW)
- `python CQr.py configure_info` - Show ClamAV setup instructions
- `python CQr.py help` - Display available commands