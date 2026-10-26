import socket
from urllib.parse import urlparse, parse_qs
from http import HTTPStatus

HOST = "127.0.0.1"
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

print(f"Сервер запущен на http://{HOST}:{PORT}")

while True:
    connection, address = server_socket.accept()
    print(f"Подключился клиент: {address}")

    data = connection.recv(4096)
    request = data.decode("utf-8")
    print(request)

    request_line = request.split("\r\n")[0]
    print("Стартовая строка:", request_line)

    method, path, version = request_line.split(" ")
    print("Метод:", method)
    print("Путь:", path)
    print("Версия:", version)

    parsed_url = urlparse(path)
    query_params = parse_qs(parsed_url.query, keep_blank_values=True)

    status_value = query_params.get("status", ["200"])[0]

    try:
        status_code = int(status_value)
        status_phrase = HTTPStatus(status_code).phrase
    except (ValueError, TypeError):
        status_code = 200
        status_phrase = HTTPStatus(status_code).phrase

    print("HTTP-статус:", status_code, status_phrase)

    headers_section = request.split("\r\n\r\n")[0]
    headers = headers_section.split("\r\n")[1:]

    print("Заголовки запроса:")
    for header in headers:
        print(header)

    response_body = (
        f"Request Method: {method}\r\n"
        f"Request Source: {address}\r\n"
        f"Response Status: {status_code} {status_phrase}\r\n"
        + "\r\n".join(headers)
    )

    print("Тело ответа:")
    print(response_body)

    body = response_body.encode("utf-8")

    response = (
        f"HTTP/1.1 {status_code} {status_phrase}\r\n"
        "Content-Type: text/plain; charset=utf-8\r\n"
        f"Content-Length: {len(body)}\r\n"
        "\r\n"
    ).encode("utf-8") + body

    connection.sendall(response)
    connection.close()