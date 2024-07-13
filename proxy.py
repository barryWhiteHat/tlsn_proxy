import socket
import threading
import ssl
import select
import subprocess 
import pdb 
import re

rust_target = "target/release/tlsn_crawle"

def extract_domains(text):
    # Regex pattern to match domain names excluding http/https and port numbers
    pattern = r'\b((?!(?:https?://|:\d{1,5}/))[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?)\b'

    # Find all matches in the text
    matches = re.findall(pattern, text)

    return matches

def handle_client_connection(client_socket):
    try:
        request = client_socket.recv(1024).decode('utf-8')
        print(f"Received request:\n{request}\n")

        # Parse the first line to get the method, URL, and HTTP version
        first_line = request.split('\n')[0]
        method, url, _ = first_line.split()

        tmp_url = extract_domains(url)[0]


        print("getting proof for ", tmp_url)        
        subprocess.Popen([rust_target, tmp_url])
       

        if method == "CONNECT":
            # Handle HTTPS connection
            handle_https_tunnel(client_socket, url)
        else:
            # Handle regular HTTP request
            handle_http_request(client_socket, method, url, request)
    
    except Exception as e:
        print (" this error ") 
        print(f"An error occurred: {e}")
        client_socket.close()

def handle_http_request(client_socket, method, url, request):
    try:
        # Extract the hostname and port
        http_pos = url.find("://")
        if http_pos == -1:
            temp = url
        else:
            temp = url[(http_pos+3):]
        
        port_pos = temp.find(":")
        
        webserver_pos = temp.find("/")
        if webserver_pos == -1:
            webserver_pos = len(temp)
        
        webserver = ""
        port = -1
        if (port_pos == -1 or webserver_pos < port_pos):
            port = 80
            webserver = temp[:webserver_pos]
        else:
            port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
            webserver = temp[:port_pos]
        
        # Create a socket to connect to the web server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((webserver, port))
        s.sendall(request.encode('utf-8'))
        
        while True:
            data = s.recv(4096)
            if (len(data) > 0):
                client_socket.send(data)
            else:
                break
        
        s.close()
        client_socket.close()
    
    except Exception as e:
        print(f"An error occurred: {e}")
        client_socket.close()

def handle_https_tunnel(client_socket, url):
    try:
        # Extract the hostname and port
        webserver, port = url.split(":")
        port = int(port)
        
        # Create a socket to connect to the web server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((webserver, port))
        
        # Respond to the client that the connection is established
        client_socket.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
        
        # Relay data between client and server
        relay_data(client_socket, s)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        client_socket.close()

def relay_data(client_socket, server_socket):
    try:
        sockets = [client_socket, server_socket]
        while True:
            readable, _, _ = select.select(sockets, [], [])
            for s in readable:
                data = s.recv(4096)
                if not data:
                    return
                if s is client_socket:
                    server_socket.sendall(data)
                else:
                    client_socket.sendall(data)
    except Exception as e:
        print(f"An error occurred while relaying data: {e}")
        client_socket.close()
        server_socket.close()

def start_proxy_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"[*] Listening on {host}:{port}")
    
    while True:
        client_socket, addr = server.accept()
        print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
        client_handler = threading.Thread(target=handle_client_connection, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    host = "127.0.0.1"  # Localhost
    port = 8080         # Port number
    start_proxy_server(host, port)

