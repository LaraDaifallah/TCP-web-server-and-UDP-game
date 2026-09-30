# TCP Web Server and UDP Multiplayer Game

A computer networks project implemented in Python using sockets, with two independent tasks.

## Task 1: TCP Web Server

A socket-based HTTP server with English and Arabic pages, CSS and image serving, file lookup, and 403/404 error pages. The server logs client addresses and request status.

### Run

Requires Python 3; uses only the standard library. Run from the task directory so the server can locate its assets:

```bash
cd task1-tcp-web-server
python server.py
```

Open http://localhost:5239/en or http://localhost:5239/ar in a browser. Stop with Ctrl+C.

## Task 2: UDP Multiplayer Number Game

A threaded UDP server and command-line client. The game starts with at least two players. Each round allows 60 seconds to submit a number from 1 to 100. Numbers already accepted during the game cannot be reused; invalid submissions and missed deadlines eliminate players. If players submit the same number, the server processes submissions in arrival order. The game ends when one or no players remain, or all numbers are used.

### Run

In one terminal:

```bash
cd task2-udp-game
python server.py
```

In at least two other terminals, run from the same directory:

```bash
python client.py
```

Enter `127.0.0.1` for a local server and a distinct username for each player. For separate machines, enter the server machine's IP address and allow UDP port 5012 through its firewall. Stop clients with Ctrl+C; restart the server for a new game.

## Technologies

- Python 3 and its standard library
- TCP and UDP sockets
- Threading and synchronization
- HTML and CSS

## Credits

Task 1 source credits: Lara Daifallah, Shatha Abualrub, and Alaa Awashra.

## Notes

This repository preserves the submitted project code. It is an educational implementation intended for local or controlled network demonstrations. IDE settings and virtual environments are excluded.
