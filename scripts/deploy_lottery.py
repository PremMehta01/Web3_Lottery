from scripts.helpful_scripts import get_account, get_contract, fund_with_link
from brownie import Lottery, config, network
import time


def deploy_lottery():
    # account = get_account(id="freecodecamp-demo-account")
    # account = get_account(index=1) # for local index >= 0 && index < 10
    account = get_account()

    # get_contract returns contract but we need to pass address so, get_contract(__).address
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )

    print("Deployed Lottery Succesfully!!")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_txn = lottery.startLottery({"from": account})
    starting_txn.wait(1)
    print("Wohoo!! Lottery Started...")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 100000000  # optional to add any amount of wei
    enter_txn = lottery.enter({"from": account, "value": value})
    enter_txn.wait(1)
    print(f"You enter lottery with ${value} wei")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # To end lottery we first need to fund the contract by LINK because requestRandomness()
    # needs LINK
    txn = fund_with_link(lottery.address)
    txn.wait(1)

    ending_txn = lottery.endLottery({"from": account})
    ending_txn.wait(1)

    # Since endLottery() send request to chain link, and after few seconds chain link
    # send random number, so till then we have to wait
    time.sleep(60)  # 60 sec
    print(f"Congrats, {lottery.recentWinner()}, you are the Winner!!!")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
