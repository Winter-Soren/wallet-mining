#include <iostream>
#include <string>
#include <curl/curl.h>
#include <bitcoin/bitcoin.hpp>

// Function to handle cURL response
size_t WriteCallback(void* contents, size_t size, size_t nmemb, void* userp)
{
    ((std::string*)userp)->append((char*)contents, size * nmemb);
    return size * nmemb;
}

// Function to check balance using BlockCypher API
uint64_t check_balance(const std::string& address)
{
    CURL* curl;
    CURLcode res;
    std::string readBuffer;
    std::string url = "https://api.blockcypher.com/v1/btc/main/addrs/" + address + "/balance";

    curl = curl_easy_init();
    if(curl) {
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);
        res = curl_easy_perform(curl);
        curl_easy_cleanup(curl);

        if(res != CURLE_OK) {
            std::cerr << "cURL error: " << curl_easy_strerror(res) << std::endl;
            return 0;
        }

        // Parse JSON response (simplified, use a JSON library for more complex parsing)
        std::size_t balance_pos = readBuffer.find("\"balance\":");
        if (balance_pos != std::string::npos) {
            std::size_t comma_pos = readBuffer.find(",", balance_pos);
            std::string balance_str = readBuffer.substr(balance_pos + 10, comma_pos - balance_pos - 10);
            return std::stoull(balance_str);
        }
    }
    return 0;
}

int main() {
    // Seed for the entropy
    bc::data_chunk seed = bc::wallet::generate_entropy(128);
    bc::wallet::word_list mnemonic = bc::wallet::create_mnemonic(seed);

    // Display the mnemonic
    std::cout << "Mnemonic: ";
    for (const auto& word : mnemonic) {
        std::cout << word << " ";
    }
    std::cout << std::endl;

    // Create the HD wallet
    bc::wallet::hd_private hd_seed = bc::wallet::hd_private(bc::wallet::to_hd_seed(mnemonic));
    bc::wallet::hd_private m44h = hd_seed.derive_private(bc::wallet::hd_first_hardened_key + 44);
    bc::wallet::hd_private m44h0h = m44h.derive_private(bc::wallet::hd_first_hardened_key);
    bc::wallet::hd_private m44h0h0h = m44h0h.derive_private(bc::wallet::hd_first_hardened_key);
    bc::wallet::hd_private account = m44h0h0h.derive_private(0);
    bc::wallet::hd_private first_key = account.derive_private(0);
    bc::wallet::payment_address payaddr = first_key.to_payment_address();

    // Display the address
    std::string address = payaddr.encoded();
    std::cout << "Address: " << address << std::endl;

    // Check balance
    uint64_t balance = check_balance(address);
    double btc_balance = balance / 1e8; // Convert from satoshis to BTC

    // Display the balance
    std::cout << "Balance: " << btc_balance << " BTC" << std::endl;

    // Store the mnemonic and address in a file if balance > 0
    if (balance > 0) {
        std::ofstream file("wallet_info.txt", std::ios::app);
        file << "Mnemonic: ";
        for (const auto& word : mnemonic) {
            file << word << " ";
        }
        file << "\nAddress: " << address << "\nBalance: " << btc_balance << " BTC\n\n";
        file.close();
    }

    return 0;
}
