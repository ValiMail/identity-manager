#!/usr/bin/env python3
"""Print information about the identity."""
import binascii
import os
import sys

from dane_discovery.identity import Identity
from cryptography.hazmat.primitives import serialization

from idlib import Bootstrap
from dane_discovery.exceptions import TLSAError


def main():
    """Top-level logic."""
    env_required = ["DANE_ID", "APP_UID", "CRYPTO_PATH"]
    for x in env_required:
        if not os.getenv(x):
            print("Missing environment variable: {}".format(x))
            sys.exit(1)
    bootstrapper = Bootstrap(os.getenv("DANE_ID"), os.getenv("CRYPTO_PATH"), os.getenv("APP_UID"))
    print("Checking DNS identity against local private key...")
    valid, why = bootstrapper.public_identity_is_valid()
    if not valid:
        print(why)
    try:
        identity = Identity(os.getenv("DANE_ID"))
        print("Identity information:\n{}".format(identity.report()))
    except TLSAError as err:
        print("Error retrieving certificate from DNS: {}".format(err))


if __name__ == "__main__":
    main()
