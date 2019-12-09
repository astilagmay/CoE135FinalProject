import socket
from threading import Thread, Lock
from multiprocessing import Queue, Lock, Process
from queue import *
import os
import sys
import struct
from timeit import default_timer as timer

#gets local ip
def get_localip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    localip = s.getsockname()[0]
    s.close()

    return localip

#send message protocol
def send_message(message, sock):
    msg_length = len(message)
    sock.send(struct.pack('!I', msg_length))
    sock.sendall(message.encode())

    #print("[MAIN] sent ", message)

#recieve message protocol
def recv_message(sock):

    #get bytes of message
    msg_length = sock.recv(4)
    msg_length, = struct.unpack('!I', msg_length)
    #print(msg_length)

    #get message
    message = b''
    while msg_length:
        data = sock.recv(msg_length)
        
        if not data:
            break

        message += data
        msg_length -= len(data)

    #decode
    message = message.decode()
    return message


#data sender
def tcp_sender(binary, sock, i, lock):

    #acquire lock
    # lock.acquire()

    #print("[TCP TRANSFER SENDER %d] sending" % i)

    #send binary files
    msg_length = len(binary)
    sock.send(struct.pack('!I', msg_length))
    sock.sendall(binary)

    #close socket
    sock.close()

    #print("[TCP TRANSFER SENDER %d] sent" % i)

    #release lock
    # lock.release()

#sender subprocess
def tcp_transfer_s(address, proc_num, filename, lock):

    lock.acquire()

    #start subprocess
    # print("[TCP TRANSFER SENDER %d] start" % proc_num)

    #make socket and connect
    tcp_port = 10000 + proc_num

    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_address = address

    #send handshake
    try:
        tcp_sock.connect((tcp_address, tcp_port)) 
        send_message("READY", tcp_sock)
        print("[TCP TRANSFER SENDER %d] connected" % proc_num)
        start_time = timer()

        #send file
        chunk_list = []
        process_list = []
        read_size = 2**24

        # print(os.getcwd())

        #send filename
        send_message(filename, tcp_sock)

        f = open(filename, "rb")

        #process chunks
        data = f.read(read_size)
        while data:
            chunk_list.append(data)
            data = f.read(read_size)

        #send chunk numbers
        send_message(str(len(chunk_list)), tcp_sock)    


        #make subprocesses
        lock2 = Lock()

        for i, binary in enumerate(chunk_list):
            p_send = Thread(target = tcp_sender, args = (binary, tcp_sock, i, lock2))
            p_send.start()
            process_list.append(p_send)

        for p in process_list:
            p.join()

        f.close()    

        #end subprocess
        elapsed_time = timer() - start_time
        print("[TCP TRANSFER SENDER %d] ALL CHUNKS SENT: %s | Elapsed time: %.2fs" % (proc_num, filename, elapsed_time))
        tcp_sock.close()  

    #ip is offline
    except Exception as e:
        print("[TCP TRANSFER SENDER %d] %s:%d: Exception %s" % (proc_num, tcp_address, tcp_port, e))
        
    lock.release()

#data receiver
def tcp_receiver(q, sock, i, lock):
    
    #acquire lock
    lock.acquire()

    # print("[TCP TRANSFER RECEIVER %d] start" % i)

    #recieve binary files
    msg_length = sock.recv(4)
    msg_length, = struct.unpack('!I', msg_length)

    message = b''
    while msg_length:
        data = sock.recv(msg_length)

        if not data:
            break

        message += data
        msg_length -= len(data)

    q.put(message)

    #close socket
    sock.close()

    # print("[TCP TRANSFER RECEIVER %d] received" % i)

    #release lock
    lock.release()

#receiver subprocess
def tcp_transfer_r(client_address, proc_num, lock):

    #start subprocess
    # print("[TCP TRANSFER RECEIVER %d] start" % proc_num)

    process_list = []
    chunk_list = []

    #create socket and connect
    tcp_port = 10000 + proc_num

    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        tcp_sock.bind(('', tcp_port))

        tcp_sock.listen(1)

        #receive handshake
        while True:
            connection, client_address = tcp_sock.accept()
            
            data = recv_message(connection)

            if data == "READY":
                #get data of other connection1
                print("[TCP TRANSFER RECEIVER %d] connected" %proc_num)
                start_time = timer()
                break

        #receive file
        filename = recv_message(connection)

        #get number of chunks
        chunk_nums = recv_message(connection)
        chunk_nums = int(chunk_nums)

        q = Queue()
        lock2 = Lock()

        #make processes
        for i in range(chunk_nums):
            p_recv = Thread(target = tcp_receiver, args = (q, connection, i, lock2))
            p_recv.start()
            process_list.append(p_recv)

        chunk_count = 0

        #get from queue
        while True:
            if chunk_count == chunk_nums:
                break

            chunk_list.append(q.get())
            chunk_count = chunk_count + 1

        for p in process_list:
            p.join()

        #write to file
        f = open("z-" + filename, "wb")

        for data in chunk_list:
            f.write(data)

        f.close()

        #end subprocess
        end_time = timer()
        elapsed_time = end_time - start_time
        print("[TCP TRANSFER RECEIVER %d] TRANSFER COMPLETE: %s  | Elapsed time: " % (proc_num, filename), elapsed_time)
        connection.close()

    except Exception as e:
        print("[TCP TRANSFER SENDER %d] %s:%d: Exception %s" % (proc_num, client_address, tcp_port, e))

#constant tcp listener
def tcp_listener(tcp_queue):

    #initialize variables
    tcp_port = 8080
    ip_list = []
    process_list = []

    #bind to local address
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.bind((get_localip(), tcp_port))

    #listen for incoming connections
    tcp_sock.listen(1)

    #constant receive
    while True:
        connection, client_address = tcp_sock.accept()

        #check for handshakes
        try:
            # #get data of other connection
            # print("\n[TCP LISTENER] Connection from ", end="")
            # print(client_address)
            
            #receive handshake
            data = recv_message(connection)
            # print('[TCP LISTENER] Received', data)
            
            #UDP handshake
            if data == "HANDSHAKE FROM UDP":
                ip_list.append(client_address[0])
                #put ip list in main
                tcp_queue.put(ip_list)

            #file transfer
            elif "FILE TRANSFER" in data:
                #get number of files
                num_files = int(''.join(i for i in data if i.isdigit()))

                lock = Lock()

                #make subprocesses
                for i in range(num_files):
                    p_transfer = Process(target = tcp_transfer_r, args = (client_address, i, lock))
                    process_list.append(p_transfer)
                    p_transfer.start()

                #terminate subprocesses
                for proc in process_list:
                    proc.join()

        #close connection
        finally:
            tcp_queue.put(ip_list)
            connection.close()

#constant listener for packets
def udp_listener(udp_queue):
    #set variables
    udp_port = 8000
    tcp_port = 8080

    #bind to local address
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(('', udp_port))

    #receive from broadcast
    while True:

        try:
            #recieve broadcast packet
            data, address = udp_sock.recvfrom(64)

            #ignore broadcast locally
            if address[0] == get_localip():
                continue

            # #get data of broadcaster
            # print("[UDP LISTENER] ", end="")
            # print(data.decode(), address)

            #send TCP handshake
            if (data.decode() != None):
                    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    tcp_address = address[0]

                    try:
                        tcp_sock.connect((tcp_address, tcp_port)) 
                        message = "HANDSHAKE FROM UDP"
                        send_message(message, tcp_sock)

                    #ip is offline
                    except Exception as e:
                        print("[UDP LISTENER] %s:%d: Exception %s" % (tcp_address, tcp_port, e))
                    
                    finally:
                        tcp_sock.close()  

        #nothing received
        except Exception as e:
            print("[UDP LISTENER] Exception %s" % e)

#gets ip list from tcp listener subprocess
def check_iplist(queue):
    #get from queue
    try:
        ip_list = queue.get(block = True, timeout = 1)  

    #queue is empty
    except:
        print("[MAIN] check_iplist timed out")
        ip_list = []
        # print("\n[MAIN] IP list is empty\n")

    return ip_list

#sends broadcast packets
def udp_broadcast():
    udp_port = 8000
    bsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    bsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    bsocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    bsocket.sendto('UDP Broadcast'.encode(), ('255.255.255.255', udp_port))

if __name__ == '__main__':

    #initialize variables
    timeout = 1
    setting = 0
    contacts = []
    ip_list = []
    tcp_port = 8080

    #initialize queue and process
    q_udp_listener = Queue()
    p_udp = Process(target = udp_listener, args = (q_udp_listener,))

    q_tcp_listener = Queue()
    p_tcp = Process(target = tcp_listener, args = (q_tcp_listener,))

    p_udp.daemon = True

    process_list = []

    #start listeners
    p_udp.start() 
    p_tcp.start() 

    file_list = []

    #choose files in current directory
    print("[FILE LIST]")
    os.chdir("..")
    files = [f for f in os.listdir('./single')]
    if ".DS_Store" in files:
        files.remove(".DS_Store")

    for f in files:
        print(f)


    file_list = files
    #print(file_list)

    if not file_list:
        print("\nNo file selected.\n")

    #broadcast to get active IPs
    udp_broadcast()

    #get ip list
    ip_list = check_iplist(q_tcp_listener)

    #empty IP list
    if not ip_list:
        ip_list = []
        print("\nIP list is empty\n")

    #non empty IP list
    else:
        print("\nSelect IP:")
        for i, ip in enumerate(ip_list):
            print("(" + str(i) + ") " + ip)

        print("")
        ip_choice = int(input(": "))

        #invalid IP
        if ip_choice > (len(ip_list) - 1):
            print("\nInvalid IP\n")

        #file transfer start
        else:
            tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            address = ip_list[ip_choice]

            try:
                tcp_sock.connect((address, tcp_port))
                message = "FILE TRANSFER " + str(len(file_list))
                send_message(message, tcp_sock)

                lock = Lock()
                os.chdir("./single")

                #make subprocesses
                for i in range(len(file_list)):
                    p_transfer = Process(target = tcp_transfer_s, args = (address, i, file_list[i], lock))
                    process_list.append(p_transfer)
                    p_transfer.start()

                #terminate subprocesses
                for proc in process_list:
                    proc.join()

            #ip is offline
            except Exception as e:
                print("%s is no longer online" % address)
                #print("%s:%d: Exception %s" % (address, tcp_port, e))
            
            finally:
                tcp_sock.close()  
