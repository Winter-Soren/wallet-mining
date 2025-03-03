import os
from hdwallet import HDWallet
from hdwallet.symbols import ETH as SYMBOL
from eth_utils import to_checksum_address
from mnemonic import Mnemonic
import requests
from web3 import Web3
import time
from datetime import datetime
from colorama import Fore, Style
from multiprocessing import Pool, cpu_count

# Define colors for each component
address_color = Fore.BLUE
balance_color = Fore.GREEN
mnemonic_color = Fore.YELLOW

# Initialize Mnemonic generator
mnemo = Mnemonic("english")

# Etherscan API URL
etherscan_url = "https://api.etherscan.io/api"

# Etherscan API key
etherscan_api_key = "X1J4BWTMTDF1XQTUPY1QA6PJ6355Q79RIT"

def connect_web3(url):
    web3 = Web3(Web3.HTTPProvider(url))
    return web3

total_threads = cpu_count()
print(f"Total number of threads available: {total_threads}")

num_threads = int(input(f"Enter the number of threads to use (1-{total_threads}): "))

# to check wallet balance for a given attempt number
def check_wallet_balance(attempt_counter):
    results = []
    for _ in range(num_threads):
        mnemonic = mnemo.generate(strength=128)  # 128 bits strength generates 12 words
        
        try:
            hdwallet = HDWallet(symbol=SYMBOL)
            hdwallet.from_mnemonic(mnemonic)
        except ValueError as e:
            print(f"Invalid mnemonic: {mnemonic}, Error: {str(e)}")
            continue

        hdwallet.from_path("m/44'/60'/0'/0/0")

        ethereum_address = to_checksum_address(hdwallet.p2pkh_address())

        results.append((attempt_counter, mnemonic, ethereum_address))

    return results

def fetch_balances(address_mnemonic_pairs):
    web3 = connect_web3(etherscan_url)
    balances = []
    for attempt_counter, mnemonic, address in address_mnemonic_pairs:
        while True:
            try:
                params = {
                    "module": "account",
                    "action": "balance",
                    "address": address,
                    "tag": "latest",
                    "apikey": etherscan_api_key
                }
                response = requests.get(etherscan_url, params=params)
                data = response.json()
                balance_wei = int(data["result"])
                balance_eth = balance_wei / 10**18  # Convert Wei to Ether
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"{current_time} Attempt #{attempt_counter} {address_color}Address: {address}{Style.RESET_ALL}, "
                      f"{balance_color}Balance: {balance_eth} ETH{Style.RESET_ALL}, "
                      f"{mnemonic_color}Mnemonic: {mnemonic}{Style.RESET_ALL}")
                balances.append((balance_eth, mnemonic, address))
                break
            except (ConnectionError, OSError) as e:
                print(f"Network error: {e}. Retrying in 10 seconds...")
                time.sleep(10)
                web3 = connect_web3(etherscan_url)
    return balances

attempt_counter = 0

# to manage parallel processing
def main():
    global attempt_counter
    with Pool(num_threads) as pool:
        while True:
            attempt_counter += num_threads
            results = pool.map(check_wallet_balance, [attempt_counter] * num_threads)
            address_mnemonic_pairs = [item for sublist in results for item in sublist]

            balances = pool.map(fetch_balances, [address_mnemonic_pairs])
            for balance, mnemonic, address in [item for sublist in balances for item in sublist]:
                if balance > 0:
                    print(f"Match found! Mnemonic: {mnemonic}")
                    print(f"Derived Ethereum Address: {address}")
                    print(f"Balance: {balance} ETH")

                    # store the wallet info in a file
                    with open("wallet_info.txt", "w") as f:
                        f.write(f"Mnemonic: {mnemonic}\n")
                        f.write(f"Address: {address}\n")
                        f.write(f"Balance: {balance} ETH\n")
                        f.write("\n")

                    return  

if __name__ == "__main__":
    main()

print("Finished.")
