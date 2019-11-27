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

            #except:
            bsocket.settimeout(None)
            print("[MAIN] No IPs found")
            p.terminate()

            break

        #view contacts
        elif (option == 3):
            break

        #add contact
        elif (option == 4):
            break

        #change settings
        elif (option == 5):

            if (setting == 0):
                print("\nReceiving from Everyone by default\n")

            elif (setting == 1):
                print("\nReceiving is Off\n")

            elif (setting == 2):
                print("\nReceiving from Contacts Only\n")

            else:
                print("\nReceiving from Everyone\n")

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
            break

        #exit
        elif (option == 6):
            print("\nExiting program")
            exit()

        #default
        else:
            print("Invalid command")


