# coding: latin-1
###############################################################################
# Copyright (c) 2023 European Commission
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###############################################################################
"""
The PID Issuer Web service is a component of the PID Provider backend. 
Its main goal is to issue the PID in cbor/mdoc (ISO 18013-5 mdoc) and SD-JWT format.

This config_countries.py contains configuration data related to the countries supported by the PID Issuer. 

NOTE: You should only change it if you understand what you're doing.
"""

from .config_service import ConfService as cfgserv


class ConfCountries:
    formCountry = "FC"
    # supported countries
    supported_countries = {
        formCountry: {
            "name": "FormEU",
            "pid_url": cfgserv.service_url + "pid/form",
            "pid_mdoc_privkey": "/opt/py-issuer/keys/py-issuer.key",
            "pid_mdoc_privkey_passwd": None,  # None or bytes
            "pid_mdoc_cert": "/opt/py-issuer/keys/py-issuer.der",
            "un_distinguishing_sign": "FC",
            "supported_credentials": [
                "eu.europa.ec.eudi.pid_mdoc",
                "eu.europa.ec.eudi.pid_jwt_vc_json",
                "eu.europa.ec.eudi.mdl_jwt_vc_json",
                "eu.europa.ec.eudi.mdl_mdoc",
                "eu.europa.ec.eudi.over18_mdoc",
                "eu.europa.ec.eudi.loyalty_mdoc",
                "eu.europa.ec.eudi.pseudonym_over18_mdoc",
                "eu.europa.ec.eudi.pseudonym_over18_mdoc_deferred_endpoint",
                "eu.europa.ec.eudi.nl.pensioenoverzicht",
            ],
            "dynamic_R2": cfgserv.service_url + "dynamic/form_R2",
        },
    }
