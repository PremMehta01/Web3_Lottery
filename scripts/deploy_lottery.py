from scripts.helpful_scripts import get_account, get_contract
from brownie import Lottery, config, network


def deploy_lottery():
    # account = get_account(id="freecodecamp-demo-account")
    # account = get_account(index=1) # for local index >= 0 && index < 10
    account = get_account()

    # get_contract returns contract but we need to pass address so, get_contract(__).address
    Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )

    print("Deployed Lottery Succesfully!!")


def main():
    deploy_lottery()
