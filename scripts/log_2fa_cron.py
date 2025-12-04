#!/usr/bin/env python3
"""
Cron script to log 2FA codes every minute.

Reads hex seed from /data/seed.txt, generates current TOTP code,
and prints a timestamped line that cron appends to /cron/last_code.txt.
"""

import sys
import datetime

from totp_utils import generate_totp_code  # you already use this in API


SEED_PATH = "/data/seed.txt"


def main() -> None:
    # 1. Read hex seed from persistent storage
    try:
        with open(SEED_PATH, "r", encoding="utf-8") as f:
            hex_seed = f.read().strip()
    except FileNotFoundError:
        print(f"{datetime.datetime.now(datetime.timezone.utc)} - Seed file not found at {SEED_PATH}", file=sys.stderr)
        return

    if not hex_seed:
        print(f"{datetime.datetime.now(datetime.timezone.utc)} - Seed file is empty at {SEED_PATH}", file=sys.stderr)
        return

    # 2. Generate current TOTP code
    try:
        code = generate_totp_code(hex_seed)
    except Exception as e:
        print(f"{datetime.datetime.now(datetime.timezone.utc)} - Failed to generate TOTP: {e}", file=sys.stderr)
        return

    # 3. Get current UTC timestamp
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    timestamp = now_utc.strftime("%Y-%m-%d %H:%M:%S")

    # 4. Output formatted line
    print(f"{timestamp} - 2FA Code: {code}")


if __name__ == "__main__":
    main()

