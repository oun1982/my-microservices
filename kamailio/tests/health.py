import socket
with socket.create_connection(('sbc-external', 5060), timeout=2):
    pass
