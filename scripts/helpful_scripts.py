from brownie import (
    network,
    accounts,
    config,
    MockV3Aggregator,
    Contract,
    VRFCoordinatorMock,
    LinkToken,
)


LOCAL_BLOCKCHAIN_ENVIRONMENT = ["development", "ganache-local"]
FORKED_LOCAL_ENVIRONMENT = ["mainnet-fork"]

# if index (accounts list index) pass return accounts[index]
# if id (account address :: can be abbreviated by name) pass return accounts.load(id)
# if env is in LOCAL_BLOCKCHAIN_ENVIRONMENT or FORKED_LOCAL_ENVIRONMENT return 0 index address from accounts
# else return address from private key
def get_account(index=None, id=None):
    if index:
        return accounts[index]

    if id:
        return accounts.load(id)

    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENT
        or network.show_active() in FORKED_LOCAL_ENVIRONMENT
    ):
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    """
    If you want to use this function, go to the brownie config and add a new entry for
    the contract that you want to be able to 'get'. Then add an entry in the variable 'contract_to_mock'.
        This script will then either:
            - Get a address from the config
            - Or deploy a mock to use for a network that doesn't have it
        Args:
            contract_name (string): This is the name that is referred to in the
            brownie config and 'contract_to_mock' variable.
        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            Contract of the type specificed by the dictionary. This could be either
            a mock or the 'real' contract on a live network.
    """

    contract_type = contract_to_mock[contract_name]

    # check if env is local or not (don't check for local forked env as for this env we need not to deploy mock)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENT:
        if (
            len(contract_type) <= 0
        ):  # check if the mock is been deploying for first time, like len(MockV3Aggregator)
            deploy_mock()

        # get the latest contract
        contract = contract_type[-1]  # e.g. MockV3Aggregator[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        # create contract by using contract_name, contract_address and abi (from MockV3Aggregator)
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )

    return contract


DECIMALS = 8
INITIAL_VALUE = 2000 * 10**8


def deploy_mock(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})

    print("Mock Contract Deployed!")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
):  # amount = 0.1LINK i.e. 10**17
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Funded contract with LINK!!")
    return tx
