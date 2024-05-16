from hdwallet import HDWallet
from hdwallet.symbols import ETH as SYMBOL
from eth_utils import to_checksum_address
from mnemonic import Mnemonic

# Given Ethereum address
given_address = "0x56822340cbf93074606a3572f92Dae67c57e1979"
given_address = to_checksum_address(given_address)

# Initialize Mnemonic generator
mnemo = Mnemonic("english")

# Counter to keep track of attempts
attempt_counter = 0

while True:
    # Step 1: Generate a random mnemonic passphrase
    mnemonic = mnemo.generate(strength=128)  # 128 bits strength generates 12 words
    print(f"Attempt #{attempt_counter}: {mnemonic}")
    
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
    # Use the public key to derive the address
    ethereum_address = hdwallet.p2pkh_address()
    print('ethereum address: ', ethereum_address)
    # Step 5: Compare with the given address
    if ethereum_address == given_address:
        print(f"Match found! Mnemonic: {mnemonic}")
        print(f"Derived Ethereum Address: {ethereum_address}")
        break  # Exit the loop
    else:
        attempt_counter += 1
        if attempt_counter % 1000 == 0:  # Print progress every 1000 attempts
            print(f"Attempts: {attempt_counter}")

print("Finished.")
