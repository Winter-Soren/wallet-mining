from hdwallet import HDWallet
from hdwallet.symbols import ETH as SYMBOL
from eth_utils import to_checksum_address
from mnemonic import Mnemonic
from web3 import Web3
import time
from colorama import Fore, Style

# Define colors for each component
address_color = Fore.BLUE
balance_color = Fore.GREEN
mnemonic_color = Fore.YELLOW

# Initialize Mnemonic generator
mnemo = Mnemonic("english")

# Initialize Web3 with Alchemy
alchemy_url = "https://mainnet.infura.io/v3/74e5288ae75f408aa9e29a5b6d114fba"  # Replace with your Alchemy API key
web3 = Web3(Web3.HTTPProvider(alchemy_url))
print("Web3 Provider:", web3.provider)
print("Web3 is connected:", web3.is_connected())

if not web3.is_connected():
    raise ConnectionError("Failed to connect to the Ethereum network")

# Counter to keep track of attempts
attempt_counter = 0

while True:
    # Step 1: Generate a random mnemonic passphrase
    mnemonic = mnemo.generate(strength=128)  # 128 bits strength generates 12 words
    # print(f"Attempt #{attempt_counter}: {mnemonic}")
    
    # Step 2: Initialize HDWallet from mnemonic
    try:
        hdwallet = HDWallet(symbol=SYMBOL)
        hdwallet.from_mnemonic(mnemonic)
    except ValueError as e:
        print(f"Invalid mnemonic: {mnemonic}, Error: {str(e)}")
        continue  # Skip to the next iteration if the mnemonic is invalid

    # Step 3: Derive the Ethereum address using BIP44 derivation path for Ethereum: m/44'/60'/0'/0/0
    hdwallet.from_path("m/44'/60'/0'/0/0")

    # Step 4: Retrieve the Ethereum address
    ethereum_address = to_checksum_address(hdwallet.p2pkh_address())

    # Step 5: Check the balance of the Ethereum address
    balance = web3.eth.get_balance(ethereum_address)
    eth_balance = web3.from_wei(balance, 'ether')

    # print the address, balance and mnemonic in color in single line
    print(f" Attempt #{attempt_counter} {address_color}Address: {ethereum_address}{Style.RESET_ALL}, "
        f"{balance_color}Balance: {eth_balance} ETH{Style.RESET_ALL}, "
        f"{mnemonic_color}Mnemonic: {mnemonic}{Style.RESET_ALL}")  
      
    if balance > 0:
        print(f"Match found! Mnemonic: {mnemonic}")
        print(f"Derived Ethereum Address: {ethereum_address}")
        print(f"Balance: {balance} wei")

        # Store the mnemonic and address in a file .txt
        with open("wallet_info.txt", "w") as f:
            f.write(f"Mnemonic: {mnemonic}\n")
            f.write(f"Address: {ethereum_address}\n")
            f.write(f"Balance: {balance} wei\n")
            f.write("\n")

        break  # Exit the loop
    else:
        attempt_counter += 1
        if attempt_counter % 1000 == 0:  # Print progress every 1000 attempts
            print(f"Attempts: {attempt_counter}")
    # Optional: Add a small delay to avoid rate limiting
    # time.sleep(0.1)

print("Finished.")
