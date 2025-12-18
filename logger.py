LOG_FILE = "log.txt"

def log(s):
    with open(LOG_FILE, "a") as f:
        f.write(s + "\n")

def log_exception(e):
    with open(LOG_FILE, "a") as f:
        f.write(f"Exception: {str(e)}\n")

def log_and_print(s):
    print(s)
    log(s)
    