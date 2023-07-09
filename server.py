import socket
import threading

# Connection Data
host = '192.168.56.102'
port = 55555

# Admin Data
admin_password = "admin"
admin_list = []

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# Dictionary for Clients and Their Nicknames
client_data = {}

# Colors for users
user_colors = {}

# ANSI escape sequences for colors
COLORS = [
    "\033[92m",  # Green
    "\033[93m",  # Yellow
    "\033[94m",  # Blue
    "\033[95m",  # Magenta
    "\033[96m",  # Cyan
    "\033[97m",  # White
    "\033[91m",  # Red
]

# Reset ANSI escape sequence
RESET_COLOR = "\033[0m"

# Sending Messages To All Connected Clients
def broadcast(message, sender_nickname):
    for client, nickname in client_data.items():
        if nickname != sender_nickname:
            color_code = get_user_color_code(sender_nickname)
            client.send("{}{}: {}{}".format(color_code, sender_nickname, message, RESET_COLOR).encode('utf-8'))

# Handling Messages From Clients
def handle(client):
    while True:
        try:

            message = client.recv(1024)
            if client_data[client] in admin_list and message.decode('utf-8').startswith('--kick '):
                nickname_to_kick = message.decode('utf-8')[7:]
                if nickname_to_kick not in admin_list:
                    kick(client, nickname_to_kick)
                else:
                    client.send("You don't have permission to kick this user!".encode('utf-8'))
            else:
                broadcast(message.decode('utf-8'), client_data[client])
        except:
            # Removing And Closing Clients
            if client_data[client] in admin_list:
                admin_list.remove(client_data[client])
            nickname = client_data[client]
            del client_data[client]
            client.close()
            broadcast('{} left!'.format(nickname), "Server")
            break

# Kicking a User
def kick(client, nickname):
    kicked_client = None
    for client, nick in client_data.items():
        if nick == nickname:
            kicked_client = client
            break

    if kicked_client is not None:
        kicked_client.send('KICK'.encode('utf-8'))
        kicked_client.close()
        del client_data[kicked_client]
        broadcast("{} был кикнут!".format(nickname), "Server")

# Receiving / Listening Function
def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        # Request And Store Nickname
        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')

        # Check if client is an administrator
        if nickname.endswith(".adm"):
            client.send('PASSWORD'.encode('utf-8'))
            password = client.recv(1024).decode('utf-8')

            if password == admin_password:
                client.send('ADMIN'.encode('utf-8'))
                nickname = "{}(Админ)".format(nickname[:-4])
                admin_list.append(nickname)
            else:
                client.send('WRONG_PASSWORD'.encode('utf-8'))
                client.close()
                break

        client_data[client] = nickname

        # Assign unique color for each user
        user_colors[nickname] = COLORS[len(user_colors) % (len(COLORS)-1)]

        # Print And Broadcast Nickname
        print("Nickname is {}".format(nickname))
        broadcast("{} joined!".format(nickname), "Server")
        client.send('Connected to server!'.encode('utf-8'))

        # Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

# Close the Server
def close_server():
    for client in client_data:
        client.close()
    server.close()

def get_user_color_code(nickname):
    if nickname in admin_list:
        return COLORS[6]  # Use color for admin
    elif nickname in user_colors:
        # color_index = len(user_colors) % len(COLORS)
        return user_colors[nickname]  # Use unique color for user
    else:
        return ""  # Default color

print("Server is listening...")
receive()
close_server()
