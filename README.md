# File Server Protection System

**Course:** Cyber Security Project

**Students:** Mohamed Ali, Rami Qaraqra

##  Project Overview

This project is a real-time security system designed to protect file servers from hosting and distributing malware. It monitors specific directories for new or modified files and automatically scans them using the **ClamAV** antivirus engine.

If a threat is detected, the system triggers an immediate response (Isolation/Logging) to prevent the infection of other users on the network.

### Key Features
* **Real-Time Monitoring:** Uses the `watchdog` library to detect "File Created" and "File Modified" events instantly.
* **Automated Scanning:** Integrates with the open-source **ClamAV Daemon** (`clamd`) for high-performance scanning.
* **Non-Blocking Architecture:** Implements `ThreadPoolExecutor` with concurrent worker threads, enabling parallel file scanning without blocking the observer.
* **Smart Startup:** Includes a "Scan on Startup" routine to detect threats that may have been introduced while the system was offline, while simultaneously monitoring for new files in real-time.


##  Prerequisites & Installation

### 1. System Requirements
* **OS:** Windows 10/11 (Project developed and tested on Windows).
* **Python:** Version 3.x.
* **Antivirus Engine:** ClamAV for Windows (running as a service).

### 2. Python Dependencies
Install the required libraries using pip:

pip install watchdog clamd


### 3\. ClamAV Setup (Windows)

1.  Download and install ClamAV.
2.  Ensure `clamd.conf` is configured with:
    ```
    TCPSocket 3310
    TCPAddr 127.0.0.1
    ```
3.  Install in terminal and start the service:
    ```bash
    clamd.exe --install
    ```
    Start service via Windows Services Manager (services.msc)
    Service Name: ClamAV ClamD
   


## How to Run

### Quick Start Example

1. **Add directories to monitor:**
   ```bash
   python CQr.py add C:\Users\YourUser\SharedFolder
   ```

2. **Start with initial scan (recommended for first run):**
   ```bash
   python CQr.py start scan
   ```
   This will:
   - Scan all existing files in your monitored directories
   - Simultaneously begin real-time monitoring for new files
   - Both operations run concurrently through the thread pool

3. **Or start with real-time monitoring only:**
   ```bash
   python CQr.py start
   ```

4. **Test:**
   - Drop a clean file into the folder → Output: `Clean`
   - Drop an EICAR test file → Output: `Infected` (file is automatically isolated)


## System Architecture

The system operates in three layers:

| Layer | Component | Description |
| :--- | :--- | :--- |
| **CLI** | `CQr.py` | Command-line interface for configuration and control. Handles user commands. |
| **Observer** | `observer.py` | Uses `watchdog` to listen for file system events. Submits scan tasks to ThreadPoolExecutor for non-blocking processing. |
| **Scanner** | `scanner.py` | Client that communicates with the local ClamAV Daemon on **Port 3310**. Returns standardized `Clean` or `Infected` status codes. |
| **Thread Pool** | `concurrent.futures.ThreadPoolExecutor` | Manages concurrent scanning workers. Handles both real-time events and initial scan tasks. |

### Execution Flow

**Real-Time Monitoring (`start` command):**
1. File system event occurs (CREATED/MODIFIED)
2. Observer detects event and submits scan task to thread pool
3. Event handler returns immediately (non-blocking)
4. Worker thread scans file while observer continues listening

**Initial Scan (`start scan` command):**
1. Observer starts and begins real-time monitoring
2. Initial scan thread walks directory tree and queues all files
3. Worker threads scan files in parallel (up to 4 simultaneously)
4. Real-time events are handled concurrently with initial scan

-----

## Project Timeline & Status

| Task | Status | Target Date |
| :--- | :--- | :--- |
| Environment Setup |  Completed | 20/12/2025 |
| Core Scanning Logic |  Completed | 01/01/2026 |
| Real-Time Monitoring |  Completed | 15/01/2026 |
| Logging & Isolation |  Completed | 25/01/2026 |
| Final Testing |  Pending | 05/02/2026 |

-----

## Known Issues / Design Decisions

* **Concurrency:** The system uses a thread pool with configurable workers (default: 4) to handle concurrent scanning. File tracking prevents duplicate scans of the same file.
* **Performance:** Implements non-blocking architecture. For extremely large files, `cd.scan_stream()` is a planned optimization for memory efficiency.
