from socket import *
from multiprocessing import Process, Queue
import os
import sys

#gets local ip
def get_localip():
    #get local ip
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    localip = s.getsockname()[0]
    s.close()

    return localip

def tcp_transfer():
    print("KEK")

#constant tcp listener
def tcp_listener(tcp_queue):
    tcp_port = 8080
    ip_list = []
    process_list = []

    #bind to local address
    tcp_sock = socket(AF_INET, SOCK_STREAM)
    tcp_sock.bind((get_localip(), tcp_port))

    #listen for incoming connections
    tcp_sock.listen(1)

    while True:
        #print("\n[TCP LISTENER] Waiting for a connection")
        connection, client_address = tcp_sock.accept()


        try:
            print("\n[TCP LISTENER] Connection from ", end="")
            print(client_address)

            # Receive the data in small chunks and retransmit it
            data = connection.recv(1024).decode()
            print('[TCP LISTENER] Received ', data)
            
            if data == "HANDSHAKE FROM UDP":
                ip_list.append(client_address[0])

            elif "FILE TRANSFER" in data:
                num_files = ''.join(i for i in data if i.isdigit())

                for i in range(num_files):
                    p_transfer = Process(target = tcp_transfer, args = (connection,client_address))
                    process_list.append(p_transfer)
                    p_transfer.start()

                for proc in process_list:
                    proc.join()

                # print("preparing for ", data)

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

        #recieve broadcast packet
        try:
            data, address = udp_sock.recvfrom(64)

            #ignore broadcast locally
            if address[0] == get_localip():
                continue

            print("[UDP LISTENER] ", end="")
            print(data.decode(), address)

            #send TCP handshake
            if (data.decode() != None):
                    tcp_sock = socket()
                    tcp_address = address[0]

                    try:
                        tcp_sock.connect((tcp_address, tcp_port)) 
                        tcp_sock.send("HANDSHAKE FROM UDP".encode())

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
    q_tcp_listener = Queue()
    p_udp = Process(target = udp_listener, args = (q_udp_listener,))
    p_tcp = Process(target = tcp_listener, args = (q_tcp_listener,))
    p_udp.daemon = True
    p_tcp.daemon = True

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
                        tcp_sock.send(message.encode())

                    #ip is offline
                    except Exception as e:
                        print("%s is no longer online" % address)
                        #print("%s:%d: Exception %s" % (address, tcp_port, e))
                    
                    finally:
                        tcp_sock.close()  


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


                


    

