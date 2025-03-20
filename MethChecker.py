import itertools
import string
import requests
import random
import os
import concurrent.futures
from colorama import Fore, Style, init

init(autoreset=True)

# get your own at https://github.com/proxifly/free-proxy-list/tree/main/proxies [http/https only]

PROXIES = {
    "http": "procksey",
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

checked_usernames = {}


def check_username_availability(username):
    if username in checked_usernames:
        return checked_usernames[username]
    
    url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    try:
        response = requests.get(url, headers=HEADERS, proxies=PROXIES, timeout=5)
    except requests.RequestException:
        return False
    
    available = response.status_code == 404
    checked_usernames[username] = available
    return available


def generate_random_usernames(count=1000, length=4, only_letters=False):
    characters = string.ascii_lowercase if only_letters else string.ascii_lowercase + string.digits + '_'
    generated = set()
    while len(generated) < count:
        username = ''.join(random.choices(characters, k=length))
        if username not in generated:
            generated.add(username)
            yield username


def find_available_usernames(length=4, filename="namesthatwork.txt", count=1000, only_letters=False):
    available_usernames = []
    total_available = 0
    
    with open(filename, "w") as file:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_username = {executor.submit(check_username_availability, username): username 
                                  for username in generate_random_usernames(count, length, only_letters)}
            
            for future in concurrent.futures.as_completed(future_to_username):
                username = future_to_username[future]
                if future.result():
                    available_usernames.append(username)
                    file.write(f"{username}\n")
                    total_available += 1
                    print(Fore.GREEN + f"[+] Available: {username}")
                else:
                    print(Fore.RED + f"[-] Taken: {username}")
    
    return available_usernames, total_available




def username_checker():
    username = input("Enter a username to check availability: ")
    if check_username_availability(username):
        print(Fore.GREEN + f"[+] The username '{username}' is available.")
    else:
        print(Fore.RED + f"[-] The username '{username}' is taken.")


def main():
    os.system("cls")
    while True:
        print("\nMeth Menu:\n\n")
        print("1. Check a specific username's" + Fore.BLUE + " availability " + Fore.RESET)
        print("2. Generate & check random" + Fore.RED + " 4C " + Fore.RESET + "usernames")
        print("3. Generate & check random" + Fore.RED + " 3C " + Fore.RESET + "usernames")
        print("4. Generate & check random" + Fore.GREEN + " 4L " + Fore.RESET + "usernames\n")
        print("5. " + Fore.RED + "Exit" + Fore.RESET)
        
        choice = input("\nEnter your choice (1, 2, 3, 4, 5): ")
        
        if choice == '1':
            username_checker()
        elif choice == '2':
            _, total_available = find_available_usernames(4, "Names_4C.txt", 1000)
            print(f"\nTotal available 4C names: {total_available}")
        elif choice == '3':
            _, total_available = find_available_usernames(3, "Names_3C.txt", 1000)
            print(f"\nTotal available 3C names: {total_available}")
        elif choice == '4':
            _, total_available = find_available_usernames(4, "Names_4L.txt", 1000, only_letters=True)
            print(f"\nTotal available 4L names: {total_available}")
        elif choice == '5':
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
