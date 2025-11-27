import ssl, socket, os

BASE = os.path.dirname(os.path.abspath(__file__))
CERTS_DIR = os.path.join(BASE, "..", "certs")
CLIENT_CERT = os.path.join(CERTS_DIR, "client_cert.pem")
CLIENT_KEY = os.path.join(CERTS_DIR, "client_key.pem")
SERVER_CA_CERT = os.path.join(CERTS_DIR, "server_cert.pem")

context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=SERVER_CA_CERT)
context.load_cert_chain(certfile=CLIENT_CERT, keyfile=CLIENT_KEY)

with socket.create_connection(("localhost", 8443)) as sock:
    with context.wrap_socket(sock, server_hostname="server.test.local") as ssock:
        ssock.send(b"Hello from client")
        data = ssock.recv(1024)
        print("Від сервера:", data.decode())
