## Introduction

This repository contains configuration to deploy the [EUDI Reference Wallet infrastructure](https://github.com/orgs/eu-digital-identity-wallet/repositories?type=all), i.e. the issuers and the verifier, in a fully containerised environment (based on [Docker](https://docs.docker.com/)). All access is with HTTPS, using [ngrok](https://ngrok.com/). This setup is prepared to use a separate trusted root CA (IACA) from the EUDI Reference Implementation.

The configuration in this repository is based on that of the official EUDI Reference Wallet repositories.

*The configuration in this repository is NOT suited for use in an production environment.*

The purpose of this to run all components on one server, and expose the interfaces over the Internet for demonstration and testing.

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
    }
    
    class pid-issuer["Issuer in Kotlin"] {
        /pid-issuer
    }

    class keycloak["keycloak as IDP"] {
        /idp
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

## How to configure and run

 1. Clone this repository
 1. Obtain a free [ngrok](https://ngrok.com/) domain (account required).
 3. Replace all occurrences of `{NGROK-DOMAIN}` with your own domain in the following files:
    - ngrok/ngrok.yml
    - haproxy/haproxy.conf
    - nginx/crl-server.conf
    - docker-compose.yaml
4. In ngrok/ngrok.yml replace `{AUTH_TOKEN}` with your ngrok authentication token.
5. Generate and configure the following certificates:
    - root certificate (if using an own root certificate; if so make sure the root certificate is included in the wallet build)
    - issuer certificate (one separate for each issuer, if so desired), issued by the CA
    - verifier certificate, issued by the CA
6. Build containers for the Python issuer and the Verifier UI. This is needed because a Docker image is not available (Python issuer) or because more flexible configuration is needed (Verifier). See [section below on how to build these containers](#how-to-build-python-issuer-and-verifier-ui-container).
7. Start the services using `docker compose up -d`

## How to build Python issuer and Verifier UI container

### Python issuer

### Verifier UI
The default Verifuer UI can only deployed on the `/` context root. As we want to deploy on `/verifier`, a minor patch is needed.

1. Clone the original [repository](https://github.com/eu-digital-identity-wallet/eudi-web-verifier).
2. Apply the patch in the verifier-ui directory of this repository to the cloned repository: 
    ```
    cd <cloned-repo>
    patch -p1 <verifier-ui>/package.json.patch
    ```
3. Build the container:
    ```
    cd <cloned-repo>
    docker build -t verifier-ui .
    ```
