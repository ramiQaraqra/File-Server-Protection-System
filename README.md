# File Server Protection System

**Course:** Cyber Security Project

**Students:** Mohamed Ali, Rami Qaraqra

##  Project Overview

This project is a real-time security system designed to protect file servers from hosting and distributing malware. It monitors specific directories for new or modified files and automatically scans them using the **ClamAV** antivirus engine.

If a threat is detected, the system triggers an immediate response (Isolation/Logging) to prevent the infection of other users on the network.

### Key Features
* **Real-Time Monitoring:** Uses the `watchdog` library to detect "File Created" and "File Modified" events instantly.
* **Automated Scanning:** Integrates with the open-source **ClamAV Daemon** (`clamd`) for high-performance scanning.
* **Concurrency Handling:** Implements a locking mechanism to prevent race conditions when multiple threads or events try to scan the same file simultaneously.
* **Smart Startup:** Includes a "Scan on Startup" routine to detect threats that may have been introduced while the system was offline.


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

1.  **Configure Paths:**
    Open `paths.txt` and add all the paths to the folders you wish to protect.

2.  **Start the Monitor:**
    Run the main monitoring script from your terminal:

    python observer.py

3.  **Test:**

      * Drop a clean file into the folder -\> Output: `Clean`.
      * Drop an EICAR test file -\> Output: `Infected`.


## System Architecture

The system operates in two layers:

| Layer | Component | Description |
| :--- | :--- | :--- |
| **Trigger** | `observer.py` | Uses `watchdog` to listen for file system events. Handles logic for **directory creation** (logging only) vs **file creation** (scanning). |
| **Scanner** | `scanner.py` | Acts as the client that communicates with the local ClamAV service on **Port 3310**. Returns standardized `Clean` or `Infected` status codes. |

-----

## Project Timeline & Status

| Task | Status | Target Date |
| :--- | :--- | :--- |
| Environment Setup |  Completed | 20/12/2025 |
| Core Scanning Logic |  Completed | 01/01/2026 |
| Real-Time Monitoring |  Completed | 15/01/2026 |
| Logging & Isolation |  In Progress | 25/01/2026 |
| Final Testing |  Pending | 05/02/2026 |

-----

## Known Issues / Design Decisions

  * **Concurrency:** To handle multiple events for the same file (e.g., specific file editors triggering 'Created' then 'Modified'), we use a `set()` to lock files currently being processed.
  * **Performance:** The system uses `cd.scan()` (synchronous). For extremely large files, `cd.scan_stream()` is the planned optimization.

<!-- end list -->
