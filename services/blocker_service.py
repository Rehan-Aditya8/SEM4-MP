import os
import json

# ===== CONSTANTS =====
HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
REDIRECT_IP = "127.0.0.1"

START_MARKER = "# === BLOCKER START ==="
END_MARKER = "# === BLOCKER END ==="

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "blocked_sites.json")


# ===== LOAD SITES =====
def load_blocked_sites():
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("Error loading blocked sites:", e)
        return []


# ===== CHECK STATUS =====
def is_block_active():
    try:
        with open(HOSTS_PATH, "r", encoding="utf-8") as file:
            return START_MARKER in file.read()
    except Exception as e:
        print("Error checking status:", e)
        return False


# ===== BLOCK WEBSITES =====
def block_websites():
    sites = load_blocked_sites()

    try:
        with open(HOSTS_PATH, "r+", encoding="utf-8") as file:
            content = file.read()

            # Prevent duplicate entries
            if START_MARKER in content:
                print("Block already active")
                return True

            file.write("\n" + START_MARKER + "\n")

            for site in sites:
                file.write(f"{REDIRECT_IP} {site}\n")

            file.write(END_MARKER + "\n")

        print("Websites blocked successfully")
        return True

    except PermissionError:
        print("Run as Administrator to modify hosts file")
        return False

    except Exception as e:
        print("Error blocking websites:", e)
        return False


# ===== UNBLOCK WEBSITES =====
def unblock_websites():
    try:
        with open(HOSTS_PATH, "r", encoding="utf-8") as file:
            lines = file.readlines()

        new_lines = []
        skip = False

        for line in lines:
            if START_MARKER in line:
                skip = True
                continue

            if END_MARKER in line:
                skip = False
                continue

            if not skip:
                new_lines.append(line)

        with open(HOSTS_PATH, "w", encoding="utf-8") as file:
            file.writelines(new_lines)

        print("Websites unblocked successfully")
        return True

    except PermissionError:
        print("Run as Administrator to modify hosts file")
        return False

    except Exception as e:
        print("Error unblocking websites:", e)
        return False


# ===== TOGGLE FUNCTION =====
def toggle_block():
    if is_block_active():
        return unblock_websites()
    else:
        return block_websites()