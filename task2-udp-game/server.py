import socket
import threading
import time

UDP_PORT = 5012
SERVER_IP = '0.0.0.0'
TIME_LIMIT = 60
MIN_PLAYERS = 2
NUMBER_RANGE = (1, 100)

clients = {}  # username: (ip, port)
used_numbers = set()
submissions = {}
lock = threading.Lock()
game_active = False
round_number = 0
running = True
current_round_message = ""  # Track the current prompt message

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((SERVER_IP, UDP_PORT))
print(f"[SERVER STARTED] Listening on port {UDP_PORT}...\n")

def broadcast(message):
    with lock:
        for user, addr in clients.items():
            udp_socket.sendto(message.encode(), addr)

def receive_loop():
    global game_active, running
    while running:
        try:
            data, addr = udp_socket.recvfrom(1024)
        except OSError:
            break  # Socket closed, exit loop

        message = data.decode().strip()

        with lock:
            if message.startswith("JOIN:"):
                username = message[5:]
                if username not in clients:
                    clients[username] = addr
                    print(f"[NEW CONNECTION] {username} joined from {addr}")
                    udp_socket.sendto("JOINED".encode(), addr)

                    # Send current round prompt immediately if game active
                    if game_active and current_round_message:
                        udp_socket.sendto(current_round_message.encode(), addr)

                    if len(clients) >= MIN_PLAYERS and not game_active:
                        threading.Thread(target=start_game).start()

            elif game_active and addr in clients.values():
                for user, user_addr in clients.items():
                    if user_addr == addr:
                        if user not in submissions:
                            try:
                                number = int(message)
                                submissions[user] = number
                            except ValueError:
                                pass
                        break

def start_game():
    global game_active, round_number, running, current_round_message
    game_active = True
    print("\n[GAME STARTED] Minimum players reached. Beginning rounds...\n")
    broadcast("Game is starting now!")

    while True:
        if len(clients) < 2:
            break

        available_numbers = set(range(NUMBER_RANGE[0], NUMBER_RANGE[1] + 1)) - used_numbers
        if not available_numbers:
            broadcast("No more unique numbers available. All remaining players are winners.")
            print("[GAME OVER] All numbers used. Remaining clients are winners.")
            print(f"Winners: {', '.join(clients.keys())}")
            break

        round_number += 1
        print(f"\n=== ROUND {round_number} ===")
        current_round_message = "New round started! Enter a number between 1 and 100:"
        broadcast(current_round_message)

        submissions.clear()
        start_time = time.time()

        while time.time() - start_time < TIME_LIMIT:
            time.sleep(1)
            with lock:
                if len(submissions) == len(clients):
                    break

        to_eliminate = []
        with lock:
            print("[SUBMISSIONS]")
            for user, number in submissions.items():
                print(f"{user} submitted: {number}")
                if number in used_numbers or not (1 <= number <= 100):
                    print(f"[INVALID] {user}'s number is already used or invalid.")
                    to_eliminate.append(user)
                else:
                    used_numbers.add(number)
                    udp_socket.sendto(f"Valid submission: {number}".encode(), clients[user])

            for user in set(clients) - set(submissions):
                print(f"[TIMEOUT] {user} did not submit in time.")
                to_eliminate.append(user)

            for user in to_eliminate:
                udp_socket.sendto("You have been eliminated.".encode(), clients[user])
                print(f"[ELIMINATED] {user} has been removed from the game.")
                del clients[user]

        broadcast(f"Round {round_number} complete. {len(clients)} players remaining.")

        if len(clients) == 1:
            winner = list(clients.keys())[0]
            broadcast(f"Game over! Winner is {winner}.")
            print(f"\n[GAME OVER] Winner is: {winner}")
            break
        elif len(clients) == 0:
            broadcast("Game over! No winners.")
            print(f"\n[GAME OVER] No winners remain.")
            break

    broadcast("Server is shutting down. Thank you for playing.")
    print("\n[SERVER SHUTDOWN] Game ended. Server shutting down.")
    running = False
    time.sleep(1)
    udp_socket.close()

threading.Thread(target=receive_loop).start()
