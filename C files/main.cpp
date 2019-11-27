#include <iostream>
#include <thread>
using namespace std;


//Features:
//Receive while sending
//Contacts only

#define broadcast_port 8080


int main() {

    int input = 0;
    int setting = 0;

    cout << "Welcome to Linux AirDrop\n";
    cout << "A CoE 115 project by Asti Lagmay\n";

    while(input != 6) {

        cout << "Please choose an option below:\n";
        cout << "(1) Send file\n";
        cout << "(2) View network IPs\n";
        cout << "(3) View contacts\n";
        cout << "(4) Add contact\n";
        cout << "(5) Change AirDrop settings\n";
        cout << "(6) Exit\n";

        cin >> input;

        switch(input) {

            //send file
            case 1: {
                break;
            }

            //view network IPs
            case 2: {
                break;
            }


            //view contacts
            case 3: {
                break;
            }

            //add contact
            case 4: {
                break;
            }
            
            //change settings
            case 5: {

                cout << "\n";

                if (setting == 0) {
                    cout << "Receiving is off by default.\n";
                }

                else if (setting == 1) {
                    cout << "Current setting: Receiving Off\n";
                }

                else if (setting == 2) {
                    cout << "Current setting: Contacts only\n"; 
                }

                else {
                    cout << "Current setting: Everyone\n";      
                }

                while(1) {

                    cout << "Please choose an option below:\n";
                    cout << "(1) Receiving Off\n";
                    cout << "(2) Contacts Only\n";
                    cout << "(3) Everyone\n";

                    cin >> setting;

                    switch(setting) {

                        case 1: {
                            cout << "Receiving is now off\n";
                            break;
                        }


                        case 2: {
                            cout << "Now receiving from Contacts Only\n";
                            break;
                        }

                        case 3: {
                            cout << "Now receiving from Everyone\n";
                            break;
                        }

                        default: {
                            cout << "Invalid command\n";
                            continue;
                            break;
                        }
                    }
                    break;

                }

                cout << "\n";
                break;
            }

            //exit
            case 6: {
                cout << "\n";

                cout << "Exiting program\n";


                cout << "\n";
                break;
                break;
            }


            //wrong input
            default: {
                cout << "Invalid command\n";
                break;
            }

            
        }

    }





    return 0;
}

