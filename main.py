from socket import *
from multiprocessing import Process, Queue
import os
import sys

def listener(pipe):
    
    #set variables
    # timeout_count = 0
    # timeout_limit = 5
    ip_list = []
    port = 8080

    #bind to local address
    udp_sock = socket(AF_INET, SOCK_DGRAM)
    udp_sock.bind(('', port))

    #receive from broadcast
    while True:

        #recieve broadcast packet
        try:
            data, address = udp_sock.recvfrom(64)
            #print data
            print("[LISTENER] ", end="")
            print(data.decode(), address)

            # create
            if (data.decode() != None):
                timeout_count = 0
                ip_list.append(address[0])
                pipe.put(ip_list)

        #nothing received
        except:
            continue
            # timeout_count = timeout_count + 1

        # finally:
        #     #print("[LISTENER] timeout " + str(timeout_count))
        #     if timeout_count == timeout_limit:
        #         #print("[LISTENER] closed")
                
        #         print("[LISTENER] closed, IP list: ", end="")
        #         print(ip_list)
                
        #         pipe.put("Done")
        #         #break

    pipe.close() 

def check_iplist(q_listener):

    #check if IPs are active
    try:
        data = q_listener.get(False)  

        if (data != "Done"):
            ip_list = data

        for ip in ip_list:
            tcp_sock = socket()
            address = ip

            try:
                tcp_sock.connect((address, port)) 
            
            #ip is offline
            except:
                #print("%s:%d: Exception is %s" % (address, port, e))
                #ip_list.remove(ip)
                pass
            
            finally:
                tcp_sock.close()  

    #queue is empty
    except:
        ip_list = []
        # print("\n[MAIN] IP list is empty\n")

    return ip_list


if __name__ == '__main__':

    #initialize variables
    timeout = 1
    setting = 0
    contacts = []
    ip_list = []
    port = 8080

    #initialize queue and process
    q_listener = Queue()
    p = Process(target = listener, args = (q_listener,))
    p.daemon = True

    #start listener
    p.start() 

    while(True):
        # print menu options
        print("Choose a command:")
        print("(1) Send file")
        print("(2) View network IPs")
        print("(3) View contacts")
        print("(4) Add contact")
        print("(5) Change AirDrop settings")
        print("(6) Exit")
        option = int(input(": "))

        #send file - NOT DONE
        if (option == 1):
            ip_list = check_iplist(q_listener)

            if not ip_list:
                ip_list = []
                print("\nIP list is empty\n")

            else:
                print("\nSelect IP:")
                for i, ip in enumerate(ip_list):
                    print("(" + str(i) + ") " + ip)

                print("")
                ip_choice = int(input(": "))

                if ip_choice > (len(ip_list) - 1):
                    print("\nInvalid IP\n")
                    continue

        #view network IPs - NOT DONE
        elif (option == 2):
            ip_list = check_iplist(q_listener)

            if not ip_list:
                ip_list = []
                print("\nIP list is empty\n")

            else:
                print("\nIP list: ")

                for ip in ip_list:
                    print(ip)

                print("")

                #print("\n")

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
            p.terminate()
            p.join()
            print("Exiting program")
            exit()

        #default
        else:
            print("Invalid command")


                


    

