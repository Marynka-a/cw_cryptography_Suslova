from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from datetime import datetime, timedelta
import os, sys

ROOT = os.path.abspath(os.getcwd())   # /app
CERTS = os.path.join(ROOT, "certs")
INTER_KEY = os.path.join(CERTS, "intermediate", "intermediate_key.pem")
INTER_CERT = os.path.join(CERTS, "intermediate", "intermediate_cert.pem")
SERVER_DIR = os.path.join(CERTS, "server")
os.makedirs(SERVER_DIR, exist_ok=True)

def error(msg):
    print(msg)
    sys.exit(1)

# check intermediate exists
if not os.path.exists(INTER_KEY) or not os.path.exists(INTER_CERT):
    error("Intermediate CA не знайдено. Спочатку створіть Root і Intermediate CA.")

with open(INTER_KEY, "rb") as f:
    intermediate_key = serialization.load_pem_private_key(f.read(), password=None)
with open(INTER_CERT, "rb") as f:
    intermediate_cert = x509.load_pem_x509_certificate(f.read())

# generate server key
key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
with open(os.path.join(SERVER_DIR, "server_key.pem"), "wb") as f:
    f.write(key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))

subject = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "UA"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Test Server"),
    x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
])

cert = (x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(intermediate_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .sign(intermediate_key, hashes.SHA256())
)

with open(os.path.join(SERVER_DIR, "server_cert.pem"), "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

print("Server Certificate створено!")
