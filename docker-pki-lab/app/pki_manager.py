import os
import subprocess
import logging

# -----------------------------
#  COLOR OUTPUT
# -----------------------------
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    GREEN = Fore.CYAN
    YELLOW = Fore.YELLOW
    RED = Fore.RED
    WHITE = Fore.WHITE
except:
    # fallback, якщо colorama не встановлено
    GREEN = YELLOW = RED = WHITE = ""

# -----------------------------
#  LOGGING
# -----------------------------
logging.basicConfig(
    filename="pki.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def log_info(msg):
    logging.info(msg)
    print(GREEN + msg)


def log_error(msg):
    logging.error(msg)
    print(RED + msg)


# -----------------------------
#  Execute Python scripts
# -----------------------------
def run_script(script_name):
    """Запуск Python-скриптів у поточному каталозі."""
    log_info(f"Запуск: {script_name}")

    try:
        subprocess.run(["python", script_name], check=True)
        log_info(f"[OK] Скрипт виконано: {script_name}")
    except subprocess.CalledProcessError:
        log_error(f"[ПОМИЛКА] Не вдалося виконати: {script_name}")


# -----------------------------
#  CLIENT CERT GENERATION
# -----------------------------
def generate_client_cert():
    """Створюємо простий клієнтський сертифікат."""
    try:
        log_info("Генерація клієнтського сертифіката...")

        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        import datetime

        CERTS_DIR = "../certs"

        # Генерація ключа
        client_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

        with open(f"{CERTS_DIR}/client_key.pem", "wb") as f:
            f.write(client_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))

        # Завантаження Intermediate CA
        with open(f"{CERTS_DIR}/intermediate/intermediate_cert.pem", "rb") as f:
            intermediate_cert = x509.load_pem_x509_certificate(f.read())

        from cryptography.hazmat.primitives.serialization import load_pem_private_key
        with open(f"{CERTS_DIR}/intermediate/intermediate_key.pem", "rb") as f:
            intermediate_key = load_pem_private_key(f.read(), password=None)

        # CSR
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "UA"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "PKI Client"),
            x509.NameAttribute(NameOID.COMMON_NAME, "client.example.com"),
        ])

        csr = x509.CertificateSigningRequestBuilder().subject_name(subject).sign(
            client_key, hashes.SHA256()
        )

        # Підпис сертифіката
        client_cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(intermediate_cert.subject)
            .public_key(client_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
            .add_extension(
                x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH]),
                critical=False
            )
            .sign(intermediate_key, hashes.SHA256())
        )

        with open(f"{CERTS_DIR}/client_cert.pem", "wb") as f:
            f.write(client_cert.public_bytes(serialization.Encoding.PEM))

        log_info("Клієнтський сертифікат успішно створено.")

    except Exception as e:
        log_error(f"Помилка створення клієнтського сертифіката: {e}")


# -----------------------------
#  VERIFY CHAIN
# -----------------------------
def verify_chain():
    try:
        log_info("Перевірка ланцюга сертифікатів...")

        from cryptography import x509

        CERTS_DIR = "../certs"

        with open(f"{CERTS_DIR}/server_cert.pem", "rb") as f:
            server = x509.load_pem_x509_certificate(f.read())

        with open(f"{CERTS_DIR}/intermediate/intermediate_cert.pem", "rb") as f:
            inter = x509.load_pem_x509_certificate(f.read())

        with open(f"{CERTS_DIR}/root_ca_cert.pem", "rb") as f:
            root = x509.load_pem_x509_certificate(f.read())

        print(GREEN + "\n=== Результат перевірки ===")
        print(WHITE + "Сервер видав:        ", server.issuer.rfc4514_string())
        print(WHITE + "Intermediate subject:", inter.subject.rfc4514_string())
        print(WHITE + "Intermediate видав:  ", inter.issuer.rfc4514_string())
        print(WHITE + "Root subject:        ", root.subject.rfc4514_string())

        log_info("Ланцюг сертифікатів перевірено.")

    except Exception as e:
        log_error(f"Помилка перевірки ланцюга: {e}")


# -----------------------------
#  MAIN MENU
# -----------------------------
def main():
    while True:
        print(YELLOW + """
==========================
       PKI MANAGER
==========================
1. Створити Root CA
2. Створити Intermediate CA
3. Згенерувати Server Certificate
4. Згенерувати Client Certificate
5. Перевірити ланцюг сертифікатів
0. Вийти
==========================
""")

        choice = input(WHITE + "Ваш вибір: ")

        if choice == "1":
            run_script("init_root_ca.py")

        elif choice == "2":
            run_script("init_intermediate_ca.py")

        elif choice == "3":
            run_script("generate_server_cert.py")

        elif choice == "4":
            generate_client_cert()

        elif choice == "5":
            verify_chain()

        elif choice == "0":
            log_info("Завершення роботи PKI Manager.")
            break

        else:
            print(RED + "Невірний вибір!")

if __name__ == "__main__":
    main()
