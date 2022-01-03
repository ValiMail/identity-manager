#!/usr/bin/env python3
"""Generate and print a TLSA record to screen."""
import os
import sys

from idlib import Bootstrap


def main():
    """Top-level logic."""
    env_required = ["DANE_ID", "APP_UID", "CRYPTO_PATH"]
    for x in env_required:
        if not os.getenv(x):
            print("Missing environment variable: {}".format(x))
            sys.exit(1)
    bootstrapper = Bootstrap(os.getenv("DANE_ID"), os.getenv("CRYPTO_PATH"),
                             os.getenv("APP_UID"))
    if os.getenv("NO_DNSSEC"):
        tlsa_record = bootstrapper.render_tlsa_record(4)
    else:
        tlsa_record = bootstrapper.render_tlsa_record(3)
    print("TLSA record for {}: {}".format(os.getenv("DANE_ID"), tlsa_record))


if __name__ == "__main__":
    main()
