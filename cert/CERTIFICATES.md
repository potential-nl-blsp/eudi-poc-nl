## HOW TO issuer and verifier certificates

### Preliminary
Create a work directory to store the certificates, keys, config files and CRL.

In the work directory:
```
touch index.txt
echo 1420 > serial
echo 1001 > crl/crlnumber
mkdir ca crl
```

### Generate root CA key and certificate
If you want to use a self-managed root certificate, then follow the instructions directly below. If you use an external CA, then skip this section, and instead of following the instructions for [creating a certificate](#generate-verifier-or-issuer-certificate-as-the-ca) send the certificate service request to the external CA as per established procedure.

Adapt `{ISSUER_URL}` in the configuration file `cert/root.cnf` to an appropriate values.

```
openssl ecparam -name secp384r1 -genkey -noout -out ca/root-ca.key
openssl ec -aes256 -in ca/root-ca.key -out ca/root-ca_encrypted.key
openssl req -config cert/root.cnf -new -x509 -key ca/root-ca.key -out ca/root-ca.crt -extensions v3_ca
```

### Generate verifier or issuer key and certificate request
Adapt the key and certificate request file names according to the role (issuer, verifier) for which you are generating them.
```
openssl ecparam -name prime256v1 -out verifier.key -genkey
openssl ec -aes256 -in verifier.key -out verifier_encrypted.key
openssl req -key verifier_encrypted.key -out verifier.csr -config cert/verifier.cnf -new
```

### generate verifier or issuer certificate as the CA
NOTE: the EUDIW has requirements on certificate validity
```
openssl ca -config cert/root.cnf -extensions v3_req -key ca/root-ca_encrypted.key -cert ca/root-ca.crt -days 360 -in verifier.csr -out verifier.crt
```

### Convert cerficate to DER-encoding (needed for Python issuer)
```
openssl x509 -in py-issert.crt -outform der -out py-issuer.der
```

### Package verifier or issuer certifcate as PKCS12 archive
Adapt the file names according to the role (issuer, verifier) for which you are generating. Choose an appropriate keystore and private key password.
```
cat verifier.crt ca/root-ca.crt > verifier-chain.pem
openssl pkcs12 -export -name verifier -inkey verifier_encrypted.key -in verifier.crt -certfile verifier-chain.pem -out verifier.p12 -passout pass:your_password
chmod 644 verifier.p12
```

### Generate CRL
```
openssl ca -config root.cnf -gencrl -out crl/eudiw-poc-nl-root-ca-01.crl
```

### Revoke an issued certificate
```
openssl ca -config root.cnf -revoke verifier.crt
```