## Overview
This directory contains configuration for an additional example attestation for the Python issuer.
The example attestation deals with pension rights in NL and is modelled after data that might be issued by a pension fund.

### Configuration
1. Apply the following patches:
   ```
   cd <eudi-poc-nl-local-repo>
   patch -p1 < extras/pensioenoverzicht/config_service.py.patch
   patch -p1 < extras/pensioenoverzicht/config_countries.py.patch
   ```
2. Copy the attestation schema.
   ```
   cd <eudi-poc-nl-local-repo>
   cp extras/pensioenoverzicht/pensioenoverzicht.json py-issuer/config/metadata_config/credentials_supported/
   ```
3. (Re-)start the Python issuer.

### Presentation definition
The file `extras/pensioenoverzicht/presentation_definition.json` contains a presentation definition file that you can paste in the verifier web UI "Custom request" section to request presentation of the attestation.