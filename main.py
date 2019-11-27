from socket import *
from multiprocessing import Process, Pipe

def listener(conn):

    print("In process")

    while(1):
        s = socket(AF_INET, SOCK_DGRAM)
        s.bind(('',54545))
        data, address = s.recvfrom(64)
        # print(data, address)
        conn.send([data.decode(), address])

        #break

        if (data == 'kold'):
            conn.close()

if __name__ == '__main__':
    main_conn, listener_conn = Pipe()
    p = Process(target = listener, args = (listener_conn,))
    p.start()
    
    bsocket = socket(AF_INET, SOCK_DGRAM)
    bsocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    bsocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    bsocket.sendto('UDP Broadcast'.encode(), ('255.255.255.255', 54545))

    receiver = main_conn.recv()[1][0]   # prints "[42, None, 'hello']"
    ip = receiver[0]
    port = receiver[1]

    bsocket.sendto('kold'.encode(), (ip, port))
    p.join()


