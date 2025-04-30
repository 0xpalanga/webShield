import os
import platform
import socket
import subprocess
import sys
import time
import requests
import colorama
from colorama import *
import pyfiglet

colorama.init(autoreset=True)

def restart_on_fail():
    print("")
    print(f"Restarting....")
    time.sleep(3)
    main()



def install_module(module_name):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
    except Exception as e:
        print(f"Failed to install {module_name}: {e}")


def check_and_install_modules():
    required_modules = [
        "os", "socket", "sys", "time", "requests", "colorama", "pyfiglet"
    ]
    print(f"{Fore.LIGHTMAGENTA_EX}=============== Checking Library ===================")
    for module in required_modules:
        try:
            __import__(module)
            print(f"{Fore.LIGHTGREEN_EX}{module}: "+f"{Fore.LIGHTBLUE_EX} is already installed.")
            time.sleep(0.3)
        except ImportError:
            print(f"{Fore.LIGHTGREEN_EX} {module}: "+f"{Fore.LIGHTRED_EX}is not installed. Installing now...")
            if module != "os" and module != "sys" and module != "socket" and module != "time":
                install_module(module)
    print(" ")
    print(f"{Fore.GREEN} [+] All necessary modules are installed, proceeding...\n")
    




def check_os():
    os_name = os.name  
    system_name = platform.system()
    print(f"{Fore.LIGHTCYAN_EX}============= Detecting Operating System ===============")
    print("")
    if os_name == "nt":
        print("Operating System: "f"{Fore.RED}Windows and Not Supported Try Linux!")
        sys.exit(f"{Fore.RED} Exiting...")
    elif os_name == "posix":
        if system_name == "Darwin":
            print("Operating System: "+f"{Fore.LIGHTMAGENTA_EX}macOS (Apple)\n")
            sys.exit(f"{Fore.RED} Exiting...")
        elif system_name == "Linux":
            print("Operating System: "+f"{Fore.LIGHTMAGENTA_EX}Linux\n")
        else:
            print("Operating System: "+f"{Fore.LIGHTMAGENTA_EX}Unix-like, but not Linux or MacOS")
    else:
        print(f"{Fore.RED}Unknown Operating System")
        sys.exit(f"{Fore.RED} Exiting...")



def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def colorful_logo_terminal(text, foreground_color=Fore.WHITE, background_color=Back.BLACK):
    print(foreground_color + background_color + pyfiglet.figlet_format(text) + Style.RESET_ALL)

def check_host_alive(target_host):
    if target_host.startswith("http://") or target_host.startswith("https://"):
        url_for_requests = target_host
    else:
        url_for_requests = "http://" + target_host
    
    print(f"{Fore.LIGHTBLUE_EX}Checking " + f'{Fore.LIGHTGREEN_EX}{target_host}' + f"{Fore.LIGHTBLUE_EX} alive or dead\n")
    try:
        global hostByIP
        hostByIP = socket.gethostbyname(target_host)
        #print(f"Target host IP is {hostByIP}")
    except socket.gaierror as e:
        print(f"{Fore.RED}Can't get IP of {target_host} with error {e}")
        restart_on_fail()

    
    try:
        check_host = requests.get(url_for_requests)
        if check_host.status_code == 200:
            print(f"Target Host is Alive with Ip: {Fore.LIGHTCYAN_EX}{hostByIP} \n")
            return True
        else:
            print(f"{Fore.LIGHTRED_EX}Target host is not alive or invalid host or IP! \n")
            restart_on_fail()
    except requests.RequestException:
        print(f"{Fore.LIGHTRED_EX}Error occurred while trying to reach the host. It may be down or incorrect.\n")
        restart_on_fail()

def display_menu():
    print(f"{Fore.LIGHTMAGENTA_EX}===============================================================")
    print(f"{Fore.GREEN}Select Scan Options Below")
    print("""
    1. Port Scan
    2. Network Scan
    3. Nmap Script Scan
    4. Vulnerability Scan (approx 15 min)
    5. All Scan (30 minutes approx.)
    6. Change Target Host
    7. Exit
    """)

def perform_scan(target_host, scan_type):
    #nmapAutomator_dir = os.path.join(os.path.dirname(__file__), 'nmapAutomator')
    #os.chdir(nmapAutomator_dir)
    os.system(f"cd scan/ && bash scan-script.sh {target_host} {scan_type}")

def main():
    global target_host
    global hostByIP
    while True:
        clear_screen()
        print("Welcome to WebShield ")
        colorful_logo_terminal("WebShield ", Fore.LIGHTGREEN_EX)
        print("")
        check_os()
        check_and_install_modules()
        target_host = input("Enter target-host: ") 
        print(" ")
        
        if not check_host_alive(target_host):
            sys.exit("Exiting...")

        while True:
            display_menu()
            select = input("Enter option: ")
            
            # Determine target based on localhost
            scan_target = hostByIP if target_host == "localhost" else target_host
            
            if select == '1':
                perform_scan(scan_target, "port")
            elif select == '2':
                perform_scan(hostByIP, "Network")
            elif select == '3':
                perform_scan(scan_target, "Script")
            elif select == '4':
                perform_scan(scan_target, "vulns")
            elif select == '5':
                perform_scan(scan_target, "all")
            elif select == '6':
                main()
            elif select == '7':
                sys.exit(f"{Fore.LIGHTRED_EX}Exiting...")
            else:
                print(f"{Fore.RED}Invalid Input, please try Again !!!")

if __name__ == "__main__":
    main()

