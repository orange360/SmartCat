import time
import json
import pandas as pd
import web3
from web3 import Web3
from web3.middleware import geth_poa_middleware

def execute_transaction(w3, config, private_key, id, method_hex, num_executions):
    for _ in range(num_executions):
        hex_64_result = f'{id:0>64x}'

        # Construct combined hex string
        combined_hex = method_hex + hex_64_result

        # Create transaction
        account = w3.eth.account.from_key(private_key)
        nonce = w3.eth.get_transaction_count(account.address, 'latest')

        gas_price_base = w3.eth.gas_price
        gas_price = int(gas_price_base * 1.5)

        transaction = {
            'to': config["contract_address"],
            'value': 0,
            'gasPrice': gas_price,
            'nonce': nonce,
            'data': combined_hex,
            'chainId': config["chain_id"]
        }

        # Hardcoded estimated gas for simplicity
        gas_limit = config["gas_limit"]
        transaction['gas'] = gas_limit

        # Sign transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

        # Send transaction
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

        # Output transaction hash
        print(f"Transaction hash ({method_hex}): {tx_hash.hex()}")

        # Wait for transaction receipt
        tx_receipt = None
        while tx_receipt is None or tx_receipt['status'] is None:
            print("Waiting for transaction receipt...")
            time.sleep(5)  # Add a delay of 5 seconds before checking the receipt again
            try:
                tx_receipt = w3.eth.get_transaction_receipt(tx_hash)
            except web3.exceptions.TransactionNotFound:
                pass

        if tx_receipt['status'] == 1:
            print("Transaction successful!")
            print("操作结束等待60秒冷却")
            time.sleep(60)
        else:
            print("Transaction failed!")

if __name__ == "__main__":
    # Load configuration from config.json
    with open("config.json", "r") as config_file:
        config = json.load(config_file)

    # Initialize web3
    w3 = Web3(Web3.HTTPProvider(config["rpc_url"]))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    # Load user parameters from Excel file
    df = pd.read_csv("user_parameters.csv", dtype=str)



    # Execute transactions based on user parameters
    for index, row in df.iterrows():
        private_key = row['Private Key']
        id_value = int(row['ID'])
        num_feed = int(row['Feed'])
        num_clean = int(row['Clean'])

        execute_transaction(w3, config, private_key, id_value, '0x350f7198', num_feed)
        execute_transaction(w3, config, private_key, id_value, '0x0ce81dfd', num_clean)
