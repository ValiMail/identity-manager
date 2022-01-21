#!/usr/bin/env python3
"""Update cert from DNS"""
# import binascii
import os
import sys
import time

from dane_discovery.identity import Identity
from cryptography.hazmat.primitives import serialization

from idlib import Bootstrap
from dane_discovery.exceptions import TLSAError


def main():
    """Validate identity against DNS, provide meaningful feedback."""
    
    # Make sure that all of our env vars are set.
    env_required = ["DANE_ID", "APP_UID", "CRYPTO_PATH"]
    for x in env_required:
        if not os.getenv(x):
            print("Missing environment variable: {}".format(x))
            time.sleep(10)
            sys.exit(1)
    bootstrapper = Bootstrap(os.getenv("DANE_ID"), os.getenv("CRYPTO_PATH"), os.getenv("APP_UID"))

    # Validate our identity against what's in DNS
    print("Checking DNS identity against local private key...")
    valid, status = bootstrapper.public_identity_is_valid()
    if not valid:
        print("Public identity and local private key not aligned. Check TTL and try again. ERR: {}".format(status))
        time.sleep(20)
        sys.exit(1)
    try:
        print("Instantiating Identity abstraction.")
        identity = Identity(bootstrapper.identity_name)
        print("Retrieving certificate from DNS.")
        dns_cert_obj = identity.get_first_entity_certificate()
        print("Extracting public key from certificate.")
        asset = dns_cert_obj.public_bytes(serialization.Encoding.PEM)
        print("Writing the certificate from DNS to the local filesystem.")
        bootstrapper.write_pki_asset(asset, "cert")
        print("Local cert now matches DNS cert.")
    except TLSAError as err:
        print("Error retrieving certificate from DNS: {}".format(err))
        time.sleep(20)
        sys.exit(1)
    # We only get here if validation passes, so now we sleep.
    sleep_forever()


def sleep_forever():
    """Just a forever loop..."""
    while True:
        time.sleep(6000)


if __name__ == "__main__":
    main()
