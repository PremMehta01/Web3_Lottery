from brownie import accounts, Lottery, config, network
from web3 import Web3


def test_entrance_fee():
    print("asd_testing...")
    account = accounts[0]
    print("asd_account: " + str(account))
    lottery = Lottery.deploy(
        config["networks"][network.show_active()]["eth_usd_price_feed"],
        {"from": account},
    )
    entrance_fee = lottery.getEntranceFee()

    assert entrance_fee > Web3.toWei(0.020, "ether")
    assert entrance_fee < Web3.toWei(0.028, "ether")
