from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime
import os

# Папка для сертифікатів Intermediate CA
intermediate_dir = "certs/intermediate"
os.makedirs(intermediate_dir, exist_ok=True)

# 1. Генерація приватного ключа Intermediate CA
intermediate_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096
)

with open(f"{intermediate_dir}/intermediate_key.pem", "wb") as f:
    f.write(intermediate_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))

# 2. Створення сертифіката Intermediate CA, підписаного Root CA
# Завантажуємо Root CA
with open("certs/root_ca_key.pem", "rb") as f:
    root_key = serialization.load_pem_private_key(f.read(), password=None)

with open("certs/root_ca_cert.pem", "rb") as f:
    root_cert = x509.load_pem_x509_certificate(f.read())

subject = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "UA"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Kyiv"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, "Kyiv"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "PKI Lab"),
    x509.NameAttribute(NameOID.COMMON_NAME, "PKI Intermediate CA"),
])

cert = x509.CertificateBuilder().subject_name(
    subject
).issuer_name(
    root_cert.subject
).public_key(
    intermediate_key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.datetime.utcnow()
).not_valid_after(
    # Сертифікат дійсний 5 років
    datetime.datetime.utcnow() + datetime.timedelta(days=1825)
).add_extension(
    x509.BasicConstraints(ca=True, path_length=0), critical=True
).sign(root_key, hashes.SHA256())

with open(f"{intermediate_dir}/intermediate_cert.pem", "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

print("Intermediate CA створено успішно!")
print(f"Приватний ключ: {intermediate_dir}/intermediate_key.pem")
print(f"Сертифікат: {intermediate_dir}/intermediate_cert.pem")
