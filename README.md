# identity-manager

Balena Block for managing DNS-bound device identity.

This Balena Block contains tools for easily generating asymmetric key pairs, Certificate Signing Requests (CSRs), self-signed certificates, and TLSA records for representing device certificates in DNS.

## What it does

This Balena Block allows you to:

* Generate an asymmetric key pair (RSA 2048)
* Generate a certificate signing request (CSR)
* Generate a self-signed certificate
* Generate a TLSA record, for publishing your device certificate in DNS.

Why publish the certificate in DNS? Making the certificate discoverable via DNS allows you to:

* Use a DNS name to identify the client device
  * Use DNS as the namespace instead of being bound to an application- or organization-internal namespace.
  * Use the [PKIX-CD](https://datatracker.ietf.org/doc/draft-wilson-dane-pkix-cd/) pattern for locating private PKI trust anchors.
    * Use the PKIX-CD pattern to support automated trust store management.
    * Use the binding between DNS and your device certificates to prevent impersonation (only you can produce DNS-bound certs for your domain).
    * Devices can participate in multiple applications, across organizations, as long as the applications accept DNS-bound identities.
* Support E2E message security, using DNS to retrieve public keys for:
  * Encrypting messages (sender/publisher uses DNS to get recipient's public key/certificate)
  * Message verification (subscriber/recipient uses DNS to retrieve sender's public key/certificate for message signature verification)

The container will print a helpful message to stdout if the device's identity is not completely (or correctly) provisioned. Once the container stops complaining, the identity is ready to be used by any service supporting DANE client identity.

## Steps for use

### Prerequisites

* A DNS domain under your control
* If the DNS domain is not protected by DNSSEC, you will need a web server for static content (Github Pages works well enough for this)

1. Create a service in your `docker-compose.yml` file as shown [below](#docker-compose).
1. Pick a DNS name for your device, or define a pattern if you're planning to represent many devices. You'll set this as the `DANE_ID` environment variable, described below.
   * Follow this pattern: `${DEVICE_ID}._device.${MYDOMAIN}`.
   * `${DEVICE_ID}` is any DNS-compatible string, and may be multiple DNS labels.
   * `${MYDOMAIN}` is a domain you own or control.
   * For example, `c90a0d441683.airquality._device.mydomain.example` might represent:
     * An air quality sensor
     * With mac address `c90a0d441683`
     * Under your control, because you own the `mydomain.example` domain.
1. Configure environment variables for the device (see [Configuration](#Configuration), below)
1. Generate the device identity (see [Instantiation](#Instantiation), below)
1. Publish the device identity (see [Publication](#Publication), below)

### Configuration

Configuration is defined in environment variables:

| Variable  | Description                                                                                                    |
|-----------|----------------------------------------------------------------------------------------------------------------|
| DANE_ID   | This is the device's DNS name.                                                                                 |
| APP_UID   | By default, the key pair will be written with UID 0 ownership. Change that by setting this to a different UID. |
| NO_DNSSEC | If this is set, it signals to the app that your zone is not protected by DNSSEC.                               |

### Instantiation

Decide how you want to represent your identity. You have two options: with or without DNSSEC. All commands below should be run inside the container.

#### With DNSSEC

If you're using DNSSEC, all you need to do in this step is to generate a self-signed identity with `./create_selfsigned_id.py`.

#### Without DNSSEC

If you're not using DNSSEC, pick one:

* Operate your own CA (easy-rsa, SaaS, self-hosted):
  * Create the key pair and CSR: `./create_id_csr.py`
  * Get the contents of the CSR: `cat ${CRYPTO_PATH}/${DANE_ID}.csr.pem`
  * Use your CA to generate a certificate from the CSR.
* **OR** Just use self-signed certificates.
  * Create the self-signed certificate: `./create_selfsigned_id.py`
  * Get the contents of the certificate: `cat ${CRYPTO_PATH}/${DANE_ID}.crt.pem`

### Publication

Use the `./generate_tlsa.py` command to create a TLSA record suitable for publishing in DNS. Take the output from this command and use your DNS server to publish a TLSA record with those contents. Depending on the DNS management interface, you may need to input the TLSA record in separate fields.

If you're using DNSSEC, the STDOUT from your container should now indicate that the identity is correctly provisioned and quietly idle.

If you're not using DNSSEC to protect the zone where the identity is hosted, you will need to publish the CA certificate (or the self-signed certificate) at a URL following this pattern: `https://device.${MYDOMAIN}/.well-known/ca/${SKI}.pem`.  Github Pages works well for this. A little more on the URL structure:

* `${MYDOMAIN}` is the same domain under which your device identity exists.
* `${SKI}` is the subjectKeyID from the CA or self-signed certificate. STDOUT from the container will give you the URL, correctly formatted, if the certificate is not correctly published.
* Here's the logic behind this part of the protocol (purely informational, just skip it if you just want to get this up and running :-) ):
  * Why not just accept what's in DNS, without DNSSEC? Because you shouldn't trust something you cannot authenticate. DNS without DNSSEC cannot be authenticated by itself, and requires another method. In the absence of DNSSEC, this protocol falls back to Web PKI (AKA the browser bundle) to authenticate the retrieval of your private PKI trust anchors (CA certificate or self-signed certificate) over HTTPS, which is then used to ensure that the certificate you're getting from the TLSA record is signed by your CA.
  * `${MYDOMAIN}`: We require organizational domain alignment to show that the owner of the device identity is also the party presenting the CA certificate.
  * The `device` label in the URL is not a typo. This is different from the `_device` label used in the device ID. Web PKI will not sign a certificate for a server name containing an underscore. This allows you to have a Web PKI-compatible hostname for conveying trust anchors, while preventing any of your actual device records from acquiring a web PKI-compatible certificate. This offers some failure zone compartmentalization.
  * Using the subjectKeyID (`${SKI}`) from the certificate in the construction of the URL allows the web server to be used as a super simple content-addressable storage system. It's just static content, and you don't have to publish one enormous bundle of all the trust anchors for your zone. This also allows you to use multiple CAs (or self-signed certificates) for your device identities.

## docker-compose

Merge this into your Balena application's `docker-compose.yml` file:

```yaml

version: "2.1"

services:
  identity-manager:
    image: gcr.io/ValiMail/identity-manager
    restart: always
    volumes:
      - "identity:/etc/dane_id"

volumes:
  identity:

```

Mount the `identity` volume into the container needing to access the private key.

## Notes

* While this is all based on standards and functionality that you can replicate with open-source technology, Valimail provides an easy interface and API for managing DNS-bound identities like this, at scale. If you want to automate the bootstrapping process, reach out to iot@valimail.com for access to the beta!