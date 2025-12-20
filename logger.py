import datetime


LOG_FILE = "log.txt"

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def _get_timestamp():
    return datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

def log(s):
    with open(LOG_FILE, "a") as f:
        timestamp = _get_timestamp()
        f.write(f"{timestamp} {s}\n")

def log_exception(e):
    log(f"EXCEPTION: {str(e)}")

def log_and_print(s):
    print(s)
    log(s)
    

def print_exception(s):
    print(f"{Colors.FAIL}{s}{Colors.ENDC}")

def print_warning(s):
    print(f"{Colors.WARNING}{s}{Colors.ENDC}")

def print_success(s):
    print(f"{Colors.GREEN}{s}{Colors.ENDC}")

def print_info(s):
    print(f"{Colors.CYAN}{s}{Colors.ENDC}")

def print_header(s):
    print(f"{Colors.HEADER}{s}{Colors.ENDC}")