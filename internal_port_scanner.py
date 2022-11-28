import socket

for port in range(1, 65535):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(("192.168.100.1", port))
    
if 0 == result:
    print(port)
    sock.close()