#!/usr/bin/env python3

import sys, os
sys.path.append("/app")

from datetime import datetime, timezone
from totp_utils import generate_totp_code

SEED_PATH = "/data/seed.txt"

def main():
    if not os.path.exists(SEED_PATH):
        print("Seed file not found")
        return

    try:
        with open(SEED_PATH, "r") as f:
            hex_seed = f.read().strip()

        code = generate_totp_code(hex_seed)

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        print(f"{timestamp} - 2FA Code: {code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

