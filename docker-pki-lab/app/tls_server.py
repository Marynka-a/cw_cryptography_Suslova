import ssl, socket, os

BASE = os.path.dirname(os.path.abspath(__file__))
CERTS_DIR = os.path.join(BASE, "..", "certs")
SERVER_CERT = os.path.join(CERTS_DIR, "server_cert.pem")
SERVER_KEY = os.path.join(CERTS_DIR, "server_key.pem")
CLIENT_CA_CERT = os.path.join(CERTS_DIR, "client_cert.pem")

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile=SERVER_CERT, keyfile=SERVER_KEY)
context.load_verify_locations(CLIENT_CA_CERT)
context.verify_mode = ssl.CERT_REQUIRED

bind_addr = ('0.0.0.0', 8443)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
    sock.bind(bind_addr)
    sock.listen(5)
    with context.wrap_socket(sock, server_side=True) as ssock:
        print("TLS-сервер запущено на порту 8443")
        conn, addr = ssock.accept()
        print("Клієнт підключено:", addr)
        data = conn.recv(1024)
        print("Отримано:", data.decode())
        conn.send(b"Hello from server")
        conn.close()
