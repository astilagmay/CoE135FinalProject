from socket import *
from multiprocessing import Process, Queue, Lock
import os
import sys
import struct

#send message protocol
def send_message(message, socket):
    msg_length = len(message)
    socket.send(struct.pack('!I', msg_length))

    socket.sendall(message.encode())

    #print("[MAIN] sent ", message)

#recieve message protocol
def recv_message(socket):

    #get bytes of message
    msg_length = socket.recv(4)
    msg_length, = struct.unpack('!I', msg_length)
    #print(msg_length)

    #get message
    message = b''
    while msg_length:
        data = socket.recv(msg_length)
        
        if not data:
            break

        message += data
        msg_length -= len(data)

    #decode
    message = message.decode()
    return message

#gets local ip
def get_localip():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    localip = s.getsockname()[0]
    s.close()

    return localip

#data sender
def tcp_sender(binary, socket, i):
    msg_length = len(binary)
    socket.send(struct.pack('!I', msg_length))
    socket.sendall(binary)
    print("[SENDER %d] DONE" % i)

#sender subprocess
def tcp_transfer_s(socket, address, proc_num, filename):

    b_list = []
    p_list = []

    #send filename
    message = "FILENAME: " + filename
    send_message(message, socket)

    #split files
    os.chdir("./Files")

    #get filesize
    size = os.stat(filename).st_size 

    #open files
    f = open (filename, "rb")

    chunks = size // 1024 + (size % 1024 > 0)

    #send chunk size
    message = str(chunks)
    send_message(message, socket)

    #initialize chunks
    for i in range(chunks):
        data = f.read(1024)
        b_list.append(data)

    #send
    for i, b_data in enumerate(b_list):
        p = Process(target = tcp_sender, args = (b_data, socket, i))
        p.start()
        p_list.append(p)

    #join all process
    for p in p_list:
        p.join()

    print(sys.getsizeof(b_list))

    #send done
    print("[TCP TRANSFER SENDER %d] All chunks sent" % proc_num)

def tcp_receiver(q, socket, i):
 #get bytes of message
    msg_length = socket.recv(4)
    msg_length, = struct.unpack('!I', msg_length)
    #print(msg_length)

    #get message
    message = b''
    while msg_length:
        data = socket.recv(msg_length)
        
        if not data:
            break

        message += data
        msg_length -= len(data)

    q.put(message)
    print("[RECEIVER %d] DONE" % i)

#receiver subprocess
def tcp_transfer_r(connection, client_address, proc_num):
    
    p_list = []
    chunk_list = []
    chunk_count = 0

    q = Queue()

    #recieve message
    message = recv_message(connection)

    #handle filename

    if "FILENAME" in message:
        message = message.replace("FILENAME: ",'')
        filename = message
        print("[TCP TRANSFER RECEIVER %d]" % proc_num, message)

        #receive chunk size
        message = recv_message(connection)
        print("[TCP TRANSFER RECEIVER %d]" % proc_num, "chunk size: " + message)
        
        chunk_num = int(message)

        print(chunk_num)

        for i in range(chunk_num):
            p = Process(target = tcp_receiver, args = (q, connection, i))
            p.start()
            p_list.append(p)

        #join all process
        for p in p_list:
            p.join()

        while True:
            try:
                data = q.get()

                if data:
                    chunk_list.append(data)
                    chunk_count = chunk_count + 1
                
                if chunk_count == chunk_num:
                    break

            except:
                pass

        # print("[TCP TRANSFER RECEIVER %d] chunks received: %d" % (proc_num, len(chunk_list)))

        # print(chunk_list)

        #convert to file
        dummy = filename.split(".")

        f = open("z" + dummy[0] + "." + dummy[1], "wb")

        for i in range(len(chunk_list)):
            f.write(chunk_list[i])

        f.close()

    #transfer done
    print("[TCP TRANSFER RECEIVER %d] Transfer done." % proc_num)
    connection.close()


#constant tcp listener
def tcp_listener(tcp_queue):

    #initialize variables
    tcp_port = 8080
    ip_list = []
    process_list = []

    #bind to local address
    tcp_sock = socket(AF_INET, SOCK_STREAM)
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

            #file transfer
            elif "FILE TRANSFER" in data:
                #get number of files
                num_files = int(''.join(i for i in data if i.isdigit()))

                #make subprocesses
                for i in range(num_files):
                    p_transfer = Process(target = tcp_transfer_r, args = (connection , client_address,i))
                    process_list.append(p_transfer)
                    p_transfer.start()

                #terminate subprocesses
                for proc in process_list:
                    proc.join()

            #put ip list in main
            tcp_queue.put(ip_list)

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
    udp_sock = socket(AF_INET, SOCK_DGRAM)
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
                    tcp_sock = socket()
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
    bsocket = socket(AF_INET, SOCK_DGRAM)
    bsocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    bsocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
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

    #menu loop
    while(True):

        # print menu options
        print("Choose a command:")
        print("(1) Send file")
        print("(2) View network IPs")
        print("(3) View contacts")
        print("(4) Add contact")
        print("(5) Change AirDrop settings")    #done
        print("(6) Exit")   #done
        option = int(input(": "))

        #send file - NOT DONE
        if (option == 1):

            file_list = []

            #choose files in current directory
            print("\nChoose file/s to transfer, type \"All\" to transfer all files or \"Done\" when finished:")
            
            print("[FILE LIST]")
            os.chdir("..")
            files = [f for f in os.listdir('./Files')]
            if ".DS_Store" in files:
                files.remove(".DS_Store")

            for f in files:
                print(f)

            while True:
                filename = input(": ")

                if filename == "Done":
                    break

                elif filename == "All":
                    file_list = files.copy()
                    break

                else:
                    file_list.append(filename)

            #print(file_list)

            if not file_list:
                print("\nNo file selected.\n")
                continue

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
                    continue

                #file transfer start
                else:
                    tcp_sock = socket()
                    address = ip_list[ip_choice]

                    try:
                        tcp_sock.connect((address, tcp_port))
                        message = "FILE TRANSFER " + str(len(file_list))
                        send_message(message, tcp_sock)

                        #make subprocesses
                        for i in range(len(file_list)):
                            p_transfer = Process(target = tcp_transfer_s, args = (tcp_sock, address, i, file_list[i]))
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

            os.chdir("./coe135project")

        #view network IPs - DONE
        elif (option == 2):

            #broadcast to get active IPs
            udp_broadcast()

            #get ip list
            ip_list = check_iplist(q_tcp_listener)

            #ip list empty
            if not ip_list:
                ip_list = []
                print("\nIP list is empty\n")

            #print IP list
            else:
                print("\nIP list: ")

                for ip in ip_list:
                    print(ip)

                print("")

        #view contacts
        elif (option == 3):

            #file exists
            if os.path.exists("contacts.txt"):
                f = open("contacts.txt", "r")
            
            #create file
            else:
                f = open("contacts.txt", "w")    

            #add contact to array
            contacts = f.read()

            #empty
            if len(contacts) == 0:
                print("\nContacts list is empty\n")

            #non-empty
            else:
                print("\nContacts list:")
                
                for i in contacts:
                    print(i)

                print("\n")

            #close file
            f.close()

        #add contact - NOT DONE
        elif (option == 4):
            break

        #change settings
        elif (option == 5):

            #show current settings
            if (setting == 0):
                print("\nReceiving is Off by default\n")

            elif (setting == 1):
                print("\nReceiving is Off\n")

            elif (setting == 2):
                print("\nReceiving from Contacts Only\n")

            else:
                print("\nReceiving from Everyone\n")

            #ask for new settings
            while(True):

                setting = int(input("New setting: "))

                if (setting == 1):
                    print("\nReceiving is now Off\n")
                    break

                elif (setting == 2):
                    print("\nNow receiving from Contacts Only\n")
                    break

                elif (setting == 3):
                    print("\nNow receiving from Everyone\n")
                    break

                else:
                    print("Invalid setting")
                    continue

        #exit
        elif (option == 6):

            print("\nClosing processes")
            
            p_udp.terminate()
            p_udp.join()

            p_tcp.terminate()
            p_tcp.join()
            
            print("Exiting program")
            exit()

        #default
        else:
            print("Invalid command")


                


    

