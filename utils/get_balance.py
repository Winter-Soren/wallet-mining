from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def get_balance(wallet_address):
    # Initialize Chrome WebDriver with headless option
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    
    driver.get("https://etherscan.io/address/" + wallet_address)
    
    # Wait for the page to load
    time.sleep(5)  # Adjust the sleep time as needed
    
    # Get the xpath of the balance
    xpath = '/html/body/main/section[3]/div[2]/div[1]/div/div/div[2]/div/div'
    
    # Get the balance element
    balance_element = driver.find_element(By.XPATH, xpath)
    
    # Get the text of the balance element
    balance = balance_element.text.split()[0]  # Extract the balance part
    
    print(f'BALANCE: {balance} ETH, Address: {wallet_address}')
    
    # Close the WebDriver
    driver.quit()
    
    return balance

# Example usage
wallet_address = '0x8d3e809fbd258083a5ba004a527159da535c8ab7'
get_balance(wallet_address)
