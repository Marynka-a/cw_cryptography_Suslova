from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime
import os

# Папка для сертифікатів
certs_dir = "certs"
os.makedirs(certs_dir, exist_ok=True)

# 1. Генерація приватного ключа Root CA
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096
)

# Збереження приватного ключа
with open(f"{certs_dir}/root_ca_key.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))

# 2. Створення самопідписаного сертифіката Root CA
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "UA"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Kyiv"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, "Kyiv"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "PKI Lab"),
    x509.NameAttribute(NameOID.COMMON_NAME, "PKI Root CA"),
])

cert = x509.CertificateBuilder().subject_name(
    subject
).issuer_name(
    issuer
).public_key(
    private_key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.datetime.utcnow()
).not_valid_after(
    # Сертифікат дійсний 10 років
    datetime.datetime.utcnow() + datetime.timedelta(days=3650)
).add_extension(
    x509.BasicConstraints(ca=True, path_length=None), critical=True,
).sign(private_key, hashes.SHA256())

# Збереження сертифіката
with open(f"{certs_dir}/root_ca_cert.pem", "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

print("Root CA створено успішно!")
print(f"Приватний ключ: {certs_dir}/root_ca_key.pem")
print(f"Сертифікат: {certs_dir}/root_ca_cert.pem")
