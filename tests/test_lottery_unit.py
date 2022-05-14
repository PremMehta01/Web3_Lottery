from brownie import accounts, Lottery, config, network, exceptions
from scripts.deploy_lottery import deploy_lottery
from web3 import Web3
import pytest
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENT,
    fund_with_link,
    get_account,
    get_contract,
)


# only test in local/development env
def test_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENT:
        pytest.skip()

    # Arrange
    lottery = deploy_lottery()

    # Act
    # since we test it in development env, so the eth price is 2000 (deploy_mock() function of helpful_scripts)
    # and entranceFee is 50$. So in 50$ we will have 50/2000 eth = 0.025eth
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()

    # Assert
    assert expected_entrance_fee == entrance_fee


def test_cant_enter_unless_lottery_started():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENT:
        pytest.skip()

    # Arrange
    lottery = deploy_lottery()
    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_start_and_enter_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENT:
        pytest.skip()

    # Arrange
    account = get_account()
    lottery = deploy_lottery()

    # Act
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})

    # Assert
    assert lottery.players(0) == account


def test_can_end_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENT:
        pytest.skip()

    account = get_account()
    lottery = deploy_lottery()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})

    fund_with_link(lottery)
    lottery.endLottery({"from": account})

    assert lottery.lottery_state() == 2  # LOTTERY_STATE.CALCULATING_WINNER


def test_can_pick_winner_correctly():
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})

    starting_bal_account = account.balance()
    balance_of_lottery = lottery.balance()

    fund_with_link(lottery)
    transaction = lottery.endLottery({"from": account})
    request_id = transaction.events["RequestedRandomness"]["requestId"]

    # see callBackWithRandomness() function inside VRFCoordinatorMock.sol file
    # why we are calling this function becoz internally requestRandomness() from endLottery
    # function calls callBackWithRandomness() function
    STATIC_RANDOM_NUM = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RANDOM_NUM, lottery.address, {"from": account}
    )

    # 777 % players.length == 777 % 3 = 0, hence the winner is 0th index
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_bal_account + balance_of_lottery
