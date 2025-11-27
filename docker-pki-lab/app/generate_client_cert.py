from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
import os,sys

ROOT = os.path.abspath(os.getcwd())
CERTS = os.path.join(ROOT, "certs")
INTER_KEY = os.path.join(CERTS, "intermediate", "intermediate_key.pem")
INTER_CERT = os.path.join(CERTS, "intermediate", "intermediate_cert.pem")

if not os.path.exists(INTER_KEY) or not os.path.exists(INTER_CERT):
    print("Intermediate CA не знайдено. Спочатку створіть Intermediate.")
    sys.exit(1)

with open(INTER_KEY, "rb") as f:
    inter_key = serialization.load_pem_private_key(f.read(), password=None)
with open(INTER_CERT, "rb") as f:
    inter_cert = x509.load_pem_x509_certificate(f.read())

os.makedirs(CERTS, exist_ok=True)

key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
with open(os.path.join(CERTS, "client_key.pem"), "wb") as f:
    f.write(key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))

subject = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "UA"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Client"),
    x509.NameAttribute(NameOID.COMMON_NAME, "client.local"),
])

cert = (x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(inter_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .sign(inter_key, hashes.SHA256())
)

with open(os.path.join(CERTS, "client_cert.pem"), "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

print("Client cert created")
