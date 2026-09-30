# Lara Daifallah 1230239
# Shatha Abualrub 1231279
# Alaa Awashra 1230009

from socket import *
import os
import urllib.parse  # added to safely decode values it's kind of IDE problem

serverPort = 5239   # (239 + 5000) = 5239
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print(f"The server is running on port {serverPort} and ready to receive requests...\n")

# Method to open files
def open_file(file_path):
    with open(file_path, 'rb') as f:
        return f.read()

# Main loop to handle incoming connections
while True:
    connectionSocket, addr = serverSocket.accept()
    ip = addr[0]
    port = addr[1]

    try:
        request = connectionSocket.recv(1024).decode()
        if not request:
            connectionSocket.close()
            continue

        parts = request.split(" ")
        file = parts[1].lstrip("/") if len(parts) > 1 else "html/main_en.html"
        status_code = "200 OK"

        if file in ["", "index.html", "main_en.html", "en"]:
            response_body = open_file("html/main_en.html")
            content_type = "text/html"

        elif file in ["ar", "main_ar.html"]:
            response_body = open_file("html/main_ar.html")
            content_type = "text/html"

        elif file.startswith("get?file="):
            # extract the filename after ?file=
            filename = file.split("get?file=", 1)[1]
            if "&" in filename:
                filename = filename.split("&", 1)[0]
            filename = urllib.parse.unquote(filename).strip()

            # decide language from query if present
            lang = "ar" if "lang=ar" in file else "en"

            # if a full URL is pasted
            if "://" in filename:
                u = urllib.parse.urlparse(filename)
                path_only = u.path.lstrip("/")
                if path_only in ["", "index.html", "main_en.html", "en"]:
                    response_body = open_file("html/main_en.html")
                    content_type = "text/html"
                    status_code = "200 OK"
                    # send and continue
                    header = f"HTTP/1.1 {status_code}\nContent-Type: {content_type}\n\n"
                    connectionSocket.send(header.encode())
                    connectionSocket.send(response_body)
                    print(f"Client: {ip}:{port} | Requested: {file} | Status: {status_code}")
                    connectionSocket.close()
                    continue
                elif path_only in ["ar", "main_ar.html"]:
                    response_body = open_file("html/main_ar.html")
                    content_type = "text/html"
                    status_code = "200 OK"
                    header = f"HTTP/1.1 {status_code}\nContent-Type: {content_type}\n\n"
                    connectionSocket.send(header.encode())
                    connectionSocket.send(response_body)
                    print(f"Client: {ip}:{port} | Requested: {file} | Status: {status_code}")
                    connectionSocket.close()
                    continue
                # else treat the URL path like a relative filename
                filename = path_only

            # simple filename search
            filename = filename.lstrip("/")

            if "private" in filename.lower():
                status_code = "403 Forbidden"
                error_page = "html/error_403_ar.html" if lang == "ar" else "html/error_403_en.html"
                response_body = open_file(error_page)
                content_type = "text/html"

            elif os.path.exists(os.path.join("html", filename)):
                response_body = open_file(os.path.join("html", filename))
                content_type = "text/html"

            elif os.path.exists(os.path.join("css", filename)):
                response_body = open_file(os.path.join("css", filename))
                content_type = "text/css"

            elif os.path.exists(os.path.join("imgs", filename)):
                response_body = open_file(os.path.join("imgs", filename))
                if filename.endswith(".jpg") or filename.endswith(".jpeg"):
                    content_type = "image/jpg"
                elif filename.endswith(".png"):
                    content_type = "image/png"
                else:
                    content_type = "application/octet-stream"

            else:
                status_code = "404 Not Found"
                error_page = "html/error_404_ar.html" if lang == "ar" else "html/error_404_en.html"
                response_body = open_file(error_page) + f"<p> ip: {ip} port: {port} </p>".encode()
                content_type = "text/html"


        # css
        elif file.endswith(".css"):
            response_body = open_file(os.path.join("css", os.path.basename(file)))
            content_type = "text/css"

        #  Images
        elif file.endswith(".jpg") or file.endswith(".jpeg"):
            response_body = open_file(os.path.join("imgs", os.path.basename(file)))
            content_type = "image/jpg"

        elif file.endswith(".png"):
            response_body = open_file(os.path.join("imgs", os.path.basename(file)))
            content_type = "image/png"

        #  html
        elif file.endswith(".html"):
            if "private" in file.lower():
                status_code = "403 Forbidden"
                if "_ar" in file:
                    response_body = open_file("html/error_403_ar.html")
                else:
                    response_body = open_file("html/error_403_en.html")
                content_type = "text/html"
            else:
                response_body = open_file(os.path.join("html", os.path.basename(file)))
                content_type = "text/html"

        #  Not Found handler 
        else:
            status_code = "404 Not Found"
            if "_ar" in file or "/ar" in file:
                response_body = open_file("html/error_404_ar.html") + f"<p> ip: {ip} port: {port} </p>".encode()
            else:
                response_body = open_file("html/error_404_en.html") + f"<p> ip: {ip} port: {port} </p>".encode()
            content_type = "text/html"

        # Send response
        header = f"HTTP/1.1 {status_code}\nContent-Type: {content_type}\n\n"
        connectionSocket.send(header.encode())
        connectionSocket.send(response_body)

        print(f"Client: {ip}:{port} | Requested: {file} | Status: {status_code}")

    except Exception:
        status_code = "404 Not Found"
        response_body = b"<html><body><h1>Error 404: Page not found</h1></body></html>" + f"<p> ip: {ip} port: {port} </p>".encode()
        header = f"HTTP/1.1 {status_code}\nContent-Type: text/html\n\n"
        connectionSocket.send(header.encode())
        connectionSocket.send(response_body)
        print(f"Client: {ip}:{port} | Requested: {file if 'file' in locals() else 'Unknown'} | Status: {status_code}")

    finally:
        connectionSocket.close()
