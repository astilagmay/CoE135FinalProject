from socket import *
from multiprocessing import Process, Pipe
import os
import sys

def checker(data):

    timeout = 1
    timeout_count = 0
    
    print("[CHECKER] ", end="")
    print(data)

    # Create a TCP/IP socket
    tcp_sock = socket(AF_INET, SOCK_STREAM)
    server_address = (data, 8000)
    print('connecting to {} port {}'.format(*server_address))
    tcp_sock.connect(server_address)

    tcp_sock.settimeout(timeout)

    while True:
        try:
            tcp_sock.send("[CHECKER] TCP")

        except:
            timeout_count = timeout_count + 1

        finally:
            print("[CHECKER] closing " + str(timeout_count))
            if timeout_count == 10:
                break
        
    tcp_sock.close()


def listener(pipe):
    #set timeout
    timeout = 1
    timeout_count = 0
    pi_list = []

    #bind to local address
    udp_sock = socket(AF_INET, SOCK_DGRAM)
    udp_sock.bind(('' , 8080))

    #receive from broadcast
    while True:

        #check active processes
        for i, pi in enumerate(pi_list):
            if (pi_list[i][0].is_alive()):
                pass
            else:
                pi_list.remove((pi_list[i][0], pi_list[i][1]))

        #set timeout
        udp_sock.settimeout(timeout)

        try:
            data, address = udp_sock.recvfrom(64)
            #print data
            print("[LISTENER] ", end="")
            print(data.decode(), address)

            # create
            if (data.decode() != None):
                timeout_count = 0

                proc = Process(target = checker, args = (address[0],))
                pi.append((proc,address[0]))
                proc.start()

            #send to main
            pipe.send([data.decode(), address])

        except:
            timeout_count = timeout_count + 1

        finally:
            print("[LISTENER] closing " + str(timeout_count))
            if timeout_count == 10:
                print(pi_list)
                break

    pipe.close() 

if __name__ == '__main__':

    #initialize variables
    timeout = 1
    setting = 0
    contacts = []
    kill_thread = 0

    #initialize pipes
    p_main, p_listener = Pipe()
    p = Process(target = listener, args = (p_listener,))

    p.start()

    # receiver = p_main.recv()
    # ip = receiver[1][0]
    # port = receiver[1][1]
    # print("[MAIN] ", end="")
    # print(ip, port)

    #menu loop
    while(True):

        # print menu options
        print("Choose a command:")
        print("(1) Send file")
        print("(2) View network IPs")
        print("(3) View contacts")
        print("(4) Add contact")
        print("(5) Change AirDrop settings")
        print("(6) Exit")
        option = input()
        option = int(option)

        #send file - NOT DONE
        if (option == 1):

            break

        #view network IPs - NOT DONE
        elif (option == 2):

            #start thread
    
            #send UDP broadcast
            bsocket = socket(AF_INET, SOCK_DGRAM)
            bsocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            bsocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
            bsocket.sendto('UDP Broadcast'.encode(), ('255.255.255.255', 54545))

            bsocket.settimeout(timeout)

            break

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
            print("\nExiting program")
            p.join()
            exit()

        #default
        else:
            print("Invalid command")


