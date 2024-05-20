import os
import time
import requests
from bitcoinlib.wallets import Wallet
from bitcoinlib.mnemonic import Mnemonic
from bitcoinlib.keys import HDKey
from colorama import Fore, Style

address_color = Fore.BLUE
balance_color = Fore.GREEN
mnemonic_color = Fore.YELLOW

blockchain_api_url = "https://blockchain.info/balance?active={address}"

mnemo = Mnemonic()

attempt_counter = 0

last_attempt_file = "last_attempt.txt"

def check_balance(address):
    response = requests.get(blockchain_api_url.format(address=address))
    if response.status_code == 200:
        data = response.json()
        return data[address]['final_balance']
    else:
        raise ConnectionError(f"Failed to fetch balance for address {address}. HTTP Status Code: {response.status_code}")

def main():
    global attempt_counter

    if os.path.exists(last_attempt_file) and os.stat(last_attempt_file).st_size != 0:
        with open(last_attempt_file, "r") as f:
            attempt_counter = int(f.read())

    while True:
        attempt_counter += 1
        mnemonic = mnemo.generate()

        seed = mnemo.to_seed(mnemonic)

        hd_key = HDKey.from_seed(seed, network='bitcoin')
        address = hd_key.address()

        try:
            balance = check_balance(address)
            btc_balance = balance / 1e8  
        except ConnectionError as e:
            print(f"Network error: {e}. Retrying in 10 seconds...")
            for i in range(10, 0, -1):
                print(f"Retrying in {i} seconds...", end='\r')
                time.sleep(1)
            continue

        current_time = time.strftime('%Y-%m-%d %H:%M:%S')

        if 0 % 100 == 0:  
            print(f"{current_time} Attempt #{attempt_counter} {address_color}Address: {address}{Style.RESET_ALL}, "
                  f"{balance_color}Balance: {btc_balance} BTC{Style.RESET_ALL}, "
                  f"{mnemonic_color}Mnemonic: {mnemonic}{Style.RESET_ALL}")

        if balance > 0:
            print(f"Match found! Mnemonic: {mnemonic}")
            print(f"Derived Bitcoin Address: {address}")
            print(f"Balance: {btc_balance} BTC")

            with open("wallet_info.txt", "a") as f:
                f.write(f"Mnemonic: {mnemonic}\n")
                f.write(f"Address: {address}\n")
                f.write(f"Balance: {btc_balance} BTC\n")
                f.write("\n")

            break  
        else:
            if attempt_counter % 1000 == 0:  
                print(f"Attempts: {attempt_counter}")
                
    print(Fore.RED + "Script finished successfully. Exiting..." + Style.RESET_ALL)

if __name__ == "__main__":
    try:
        print(Fore.BLUE + "Starting script..." + Style.RESET_ALL)
        main()
    except KeyboardInterrupt:
        print(Fore.LIGHTCYAN_EX + "Script interrupted. Saving current progress..." + Style.RESET_ALL)
        with open(last_attempt_file, "w") as f:
            f.write(str(attempt_counter))
