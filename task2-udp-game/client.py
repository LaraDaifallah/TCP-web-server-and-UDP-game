import socket
import threading

UDP_PORT = 5012
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

SERVER_IP = input("Enter server IP address: ").strip()
username = input("Enter your username: ").strip()
server_address = (SERVER_IP, UDP_PORT)

waiting_for_input = threading.Event()

def listen_for_messages():
    while True:
        try:
            data, _ = udp_socket.recvfrom(1024)
            message = data.decode()
            print(f"\n[SERVER]: {message}")
            if "Enter a number" in message:
                waiting_for_input.set()
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

def input_loop():
    while True:
        waiting_for_input.wait()
        while True:
            try:
                number = int(input("Enter your number (1-100): ").strip())
                if 1 <= number <= 100:
                    udp_socket.sendto(str(number).encode(), server_address)
                    break
                else:
                    print("Invalid input. Number must be between 1 and 100.")
            except ValueError:
                print("Please enter a valid integer.")
        waiting_for_input.clear()

udp_socket.sendto(f"JOIN:{username}".encode(), server_address)

threading.Thread(target=listen_for_messages, daemon=True).start()
threading.Thread(target=input_loop, daemon=True).start()

while True:
    pass
