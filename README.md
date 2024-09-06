## Introduction

This repository contains configuration to deploy the [EUDI Reference Wallet infrastructure](https://github.com/orgs/eu-digital-identity-wallet/repositories?type=all), i.e. the issuers and the verifier, in a fully containerised environment (based on [Docker](https://docs.docker.com/)). All access is with HTTPS, using [ngrok](https://ngrok.com/). This setup is prepared to use a separate trusted root CA (IACA) from the EUDI Reference Implementation. The purpose is to run all components on one server, and expose the interfaces over the Internet for demonstration and testing.

The configuration in this repository is based on that of the official EUDI Reference Wallet repositories.

*NOTE: The configuration in this repository is NOT suited for use in an production environment.*
*NOTE: This repository may not be maintained as the EUDI Reference Implementation matures.*

The following diagram gives an overview of the setup.

```mermaid
---
title: Overview of containers
---
classDiagram
    direction LR

    class browser { }

    class EUDIW { }
    
    class ngrok-service { 
        https://ngrok-domain
    }

    class ngrok["Ngrok agent"] {  
        *ngrok/ngrok.yml: file
    }

    class haproxy { 
        *haproxy/haproxy.conf: file
    }
    
    class verifier-ui { 
        /verifier
    }
 
    class verifier-backend {
        /ui
        /wallet
    }
    
    class py-issuer["Issuer in Python"] { 
        /
        *py-issuer/config/app_metadata/
        *py-issuer/config/metadata_config/
        *py-issuer/config/keys/
        *py-issuer/config/trusted_cas/
    }
    
    class pid-issuer["Issuer in Kotlin"] {
        /pid-issuer
    }

    class keycloak["keycloak as IDP"] {
        /idp
        *kt-issuer/keycloak/
    } 

    class crl {
        /ca
        *nginx/crl-server.conf
    }

    browser --> ngrok-service
    EUDIW --> ngrok-service
    ngrok-service -- ngrok
    ngrok -- haproxy
    haproxy -- pid-issuer
    haproxy -- keycloak
    pid-issuer .. keycloak
    haproxy -- py-issuer
    haproxy -- crl
    haproxy -- verifier-ui
    haproxy -- verifier-backend
    verifier-ui --> verifier-backend
    py-issuer --> verifier-backend
```
The setup contains the two issuers implemented in Python and Kotlin respectively. It also contains the remote verifier user interface and backend. Finally it contains a webserver for serving the CRL of the custom Certificate Authority under which the issuer and verifier certificates are issued. This custom CA's root certificate must be compiled into and packaged with the app, which requires a patch and build. Here is [guidance for the Android version of the reference implementation wallet app](#how-to-add-a-custom-root-certificate-to-the-android-wallet-app).
If you are not using a separate root certificate you should disable the CRL webserver in the above setup.

The issuer and verifier services are accessed to a web proxy, haproxy, that manages the context roots. The context roots for every service is indicated in the above diagram starting with "/". Configuration files for the respective services are indicated started with "*".

NOTE: the Kotlin-issuer uses Keycloak as an Identity Provider for the PID data, i.e. you need an account in the pid-users-realm. The default account of the reference implementation is 'tneal' with password 'password'.

NOTE: The Python-issuer uses the verifier backend when using PID authentication before issuing specific attestation (such as Age Verification attestation).

## How to build Python issuer and Verifier UI containers

### Python issuer
The Python issuer is not yet available as a Docker container, so we build one ourselves. Additionally, the issuer cannot yet be configured to use a self-deployed verifier backend, so we need to apply some patches. These patches can be omitted once [issue #42](https://github.com/eu-digital-identity-wallet/eudi-srv-web-issuing-eudiw-py/issues/42) and [issue #44](https://github.com/eu-digital-identity-wallet/eudi-srv-web-issuing-eudiw-py/issues/44) have been resolved.

1. Clone the original [repository](https://github.com/eu-digital-identity-wallet/eudi-srv-web-issuing-eudiw-py).
2. Apply the patches:
    ```
    cd <cloned-repo>
    patch -p1 < <py-issuer>/patch/route_oidc.py.patch
    patch -p1 < <py-issuer>/patch/route_oid4vp.py.patch
    ```
2. Build the container:
    ```
    cp <py-issuer>/Dockerfile .
    docker build -t py-issuer .
    ```

### Verifier UI
The default Verifier UI can only deployed on the `/` context root. As we want to deploy on `/verifier`, a minor patch is needed.

1. Clone the original [repository](https://github.com/eu-digital-identity-wallet/eudi-web-verifier).
2. Apply the patch in the verifier-ui directory of this repository to the cloned repository: 
    ```
    cd <cloned-repo>
    patch -p1 < <verifier-ui>/package.json.patch
    ```
3. Build the container:
    ```
    docker build -t verifier-ui .
    ```

## How to configure and run the services

 1. Clone this [repository](https://github.com/potential-nl-blsp/eudi-poc-nl).
     ```
     git clone https://github.com/potential-nl-blsp/eudi-poc-nl
     ```
 2. Obtain a free [ngrok](https://ngrok.com/) domain (account required).
 3. Replace all occurrences of `{NGROK_DOMAIN}` with your own domain in the following files:
    - ngrok/ngrok.yml
    - haproxy/haproxy.conf
    - nginx/crl-server.conf
    - docker-compose.yaml
    - py-issuer/config/app_config/config_service.py
    - py-issuer/config/app_config/oid_config.json
    - py-issuer/config/metadata_config/metadata_config.json
    - py-issuer/config/metadata_config/openid-configuration.json
    - cert/root.cnf (if using a self-managed CA)
    - cert/kt-issuer.cnf (if (re-)generating a self-managed Kotlin issuer certificate)
    - cert/verifier.cnf (if (re-)generating a self-managed verifier certificate)
   You can use the command
    ```
    perl -p -i -e 's/{NGROK_DOMAIN}/your.ngrok.domain/gx' ngrok/ngrok.yml haproxy/haproxy.conf nginx/crl-server.conf docker-compose.yaml py-issuer/config/app_config/config_service.py py-issuer/config/app_config/oid_config.json py-issuer/config/metadata_config/metadata_config.json py-issuer/config/metadata_config/openid-configuration.json cert/root/cnf cert/kt-issuer.cnf cert/verifier.cnf
    ```
4. In ngrok/ngrok.yml replace `{AUTH_TOKEN}` with your ngrok authentication token.
5. Generate and configure the following certificates:
    - root certificate (if using an own root certificate; if so [make sure the root certificate is included in the wallet build](#how-to-add-a-custom-root-certificate-to-the-android-wallet-app))
    - issuer certificate (one separate for each issuer, if so desired), issued by the CA
    - verifier certificate, issued by the CA
6. Configure the certificates and private keys for the issuers and verifier.
    1. Create the keys and certificates, see [these instructions](cert/CERTIFICATES.md) for one way to do this.
    2. Configure the keystores in `docker-compose.yaml`, i.e. mapping the keystore files to the container in the 'volumes' sections of
        - pid-issuer (Kotlin issuer)
           ```
           volumes:
           - {Kotlin_issuer_keystore_file_name}:/kt-issuer.p12:ro
           ```
        - 'verifier' (verifier backend)
            ```
            volumes:
            - {verifier_keystore_file_name}:/verifier.p12:ro
            ```
    3. Set the passwords for the keystores and the private keys in `docker-compose.yaml`, i.e. the following environment variables:
        - pid-issuer (Kotlin issuer):
            - ISSUER_SIGNING_KEY_KEYSTORE_PASSWORD
            - ISSUER_SIGNING_KEY_PASSWORD
        - verifier (verifier backend):
            - VERIFIER_JAR_SIGNING_KEY_KEYSTORE_PASSWORD
            - VERIFIER_JAR_SIGNING_KEY_PASSWORD
    4. For the Python issuer:
        - in py-issuer/config/trusted_cas add the root certificates (PEM-encoded with file extension .pem) of additional CAs
        - in py-issuer/config add a directory keys and put there the private key and certificate with which to sign attestations, named 'py-issuer.key' and 'py-issuer.der' respectively. The certificate must be DER-encoded.
7. Build containers for the Python issuer and the Verifier UI. This is needed because a Docker image is not available (Python issuer) or because more flexible configuration is needed (Verifier). See [the section on how to build these containers](#how-to-build-python-issuer-and-verifier-ui-container).
8. Configure the {CRL_LOCATION} in `docker-compose.yaml` in the section for the crl service, if you are using an own root certificate.
If you are NOT using an own root certificate, comment out the crl service section in `docker-compose.yaml`, and remove the nginx dependency of the haproxy service in that same file.
9. Start the services using `docker compose up -d`. Verify that all containers are running using `docker ps`; it should list 7 running containers. Stop services with `docker compose down`.
10. Access your services using https, at your Ngrok domain with context root:
    - /verifier for the verifier,
    - /pid-issuer for the Kotlin issuer,
    - / for the Python issuer.

    The API for the verifier is available at context roots /ui and /wallet. See also the above diagram.

## How to add a custom root certificate to the Android wallet app
To add a custom root certificate to the Android wallet app you need to:

1. Clone the [repository](https://github.com/eu-digital-identity-wallet/eudi-app-android-wallet-ui):
    ```
    git clone https://github.com/eu-digital-identity-wallet/eudi-app-android-wallet-ui
    ```
2. Set up an Android build environment accoring the the instructions.
3. Add the root certificate(s) you want as additional trust anchors to `resources-logic/src/main/res/raw`, as PEM-encoded file(s) with only alphanumeric characters plus _ in the file name, file name ending in .pem.
3. Add the root cerificate file(s) to the method call in `core-logic/src/dev/java/eu/europa/ec/corelogic/config/ConfigWalletCoreImpl.kt`, line 95:
    ```
    .trustedReaderCertificates(R.raw.my_root_certificate, R.raw.eudi_pid_issuer_ut))
    ```
4. Build the wallet app, using `gradlew app:packageDevRelease`.