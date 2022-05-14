from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENT,
    fund_with_link,
    get_account,
)
import pytest
import time
from brownie import network


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENT:
        pytest.skip()

    account = get_account()
    lottery = deploy_lottery()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})

    starting_account_bal = account.balance()
    starting_lottery_bal = lottery.balance()

    fund_with_link(lottery)
    lottery.endLottery({"from": account})

    # sleep because endLottery internally calls chain link functions and chain link retuns
    # random number
    time.sleep(60)  # 60sec

    assert lottery.recentWinner() == account  # since both player is account
    assert lottery.balance() == 0
    assert account.balance() == starting_account_bal + starting_lottery_bal
