import socket

# Create a UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set up the server address
# servidor = Servidor("172.20.33.241", 20002, BUFFER_SIZE)

# server_address = ('172.20.33.241', 8255)
server_address = ('172.20.57.191', 8255)

# Send data to the server
message = b"www.poroto.com"
client_socket.sendto(message, server_address)

# Receive a response from the server
buffer_size = 1024
print("res, sv")
response, server_address = client_socket.recvfrom(buffer_size)

# Print the server's response
print("Server response:", response.decode())

# Close the socket
client_socket.close()