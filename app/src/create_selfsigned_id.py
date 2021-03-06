#!/usr/bin/env python3
"""Create a self-signed identity."""
import os
import sys

from idlib import Bootstrap


def main():
    """Top-level logic."""
    env_required = ["DANE_ID", "APP_UID", "CRYPTO_PATH"]
    env_optional = ["STATE", "COUNTRY", "LOCALITY", "ORGANIZATION"]
    for x in env_required:
        if not os.getenv(x):
            print("Missing environment variable: {}".format(x))
            sys.exit(1)
    kwargs = {x.lower: os.getenv(x) for x in env_optional if os.getenv(x)}
    bootstrapper = Bootstrap(os.getenv("DANE_ID"), os.getenv("CRYPTO_PATH"),
                             int(os.getenv("APP_UID")), **kwargs)
    print("Generating private key...")
    bootstrapper.generate_private_key()
    print("Generating self-signed certificate...")
    bootstrapper.generate_selfsigned_certificate()
    print("Identity created locally. Now, run generate_tlsa.py.")
    return


if __name__ == "__main__":
    main()
