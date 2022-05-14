// SPDX-License-Identifier: MIT

pragma solidity ^0.6.6;

// Get the latest ETH/USD price from chainlink price feed
import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";

// to check any data overflow, here uint256 overflow
import "@chainlink/contracts/src/v0.6/vendor/SafeMathChainlink.sol";

// To check onlyOwner modifier, no need to define onlyOwner modifier manually after importing
// Need to configure any import '@' in brownie-config.yaml file
// Also can be use for other purpose https://docs.openzeppelin.com/contracts/4.x/api/access
import "@openzeppelin/contracts/access/Ownable.sol";

// To get verified random number, can be used for production also
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

contract Lottery is Ownable, VRFConsumerBase {
    // safe math library check uint256 for integer overflows
    using SafeMathChainlink for uint256;

    address payable[] public players;
    address payable public recentWinner;
    uint256 public usdEntryFee;

    uint256 public fee;
    bytes32 public keyhash;

    AggregatorV3Interface internal ethUsdPriceFeed;

    // 0 -> OPEN, 1-> CLOSED, 2-> CALCULATING_WINNER
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lottery_state;

    constructor(
        address _priceFeedAddress,
        address _vrfCoordinator,
        address _link,
        uint256 _fee,
        bytes32 _keyhash
    ) public VRFConsumerBase(_vrfCoordinator, _link) {
        // Minimum $50
        usdEntryFee = 50 * (10**18);
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        lottery_state = LOTTERY_STATE.CLOSED; // OR lottery_state = 1;
        fee = _fee;
        keyhash = _keyhash;
    }

    // become a player
    function enter() public payable {
        require(
            lottery_state == LOTTERY_STATE.OPEN,
            "Sorry the Lottery is inactive now!!"
        );
        // minimum usdEntryFee required to become player
        require(msg.value >= getEntranceFee(), "Not enough ETH!!");
        players.push(msg.sender);
    }

    // returns x(amount of ETH in term of wei from $50) :: $50 = x wei
    function getEntranceFee() public view returns (uint256) {
        // get current eth price
        (, int256 price, , , ) = ethUsdPriceFeed.latestRoundData();

        // convert price int256 to uint256 and multiple by 10^10
        // to make price 10^18 decimal as original price is in 10^8 decimal
        uint256 adjustedPrice = uint256(price) * 10**10; // 18 decimal

        // lets say $2000 is the current eth price, so to convert $50 to amount of eth
        // we need to 50 / 2000 but we will do (50 * 10^18) / adjustedPrice
        uint256 costToEnter = (usdEntryFee * 10**18) / adjustedPrice;
        return costToEnter;
    }

    function startLottery() public onlyOwner {
        require(
            lottery_state == LOTTERY_STATE.CLOSED,
            "Sorry cann't start new Lottery, please complete running Lottery. Good Luck!"
        );

        lottery_state = LOTTERY_STATE.OPEN;
    }

    // Select winner
    function endLottery() public onlyOwner {
        require(
            lottery_state == LOTTERY_STATE.OPEN,
            "Please start a lottery first."
        );
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;

        // Recomendation: try to use global variable while generating random
        // Below keccack256 way of regerating random in production is highly not recommended becoz it's all parameter are predictable and hence random number can be regerated(hacked)

        // keccack256 is hashing algorithms
        // % player.length is to get index within player.length

        // uint256(
        //     keccak256(
        //         abi.encodePacked(
        //             nonce, // nonce is predictable (aka, transaction number)
        //             msg.sender, // msg.sender is predictable
        //             block.difficulty, // can actually be manipulated by miners...
        //             block.timestamp // timestamp is predictable
        //         );
        //     )
        // ) % players.length;

        // Correct way of getting random
        // requestRandomness is the function from VRFConsumerBase
        // https://github.com/smartcontractkit/chainlink/blob/develop/contracts/src/v0.6/VRFConsumerBase.sol
        // Once below requestRandomness(keyhash, fee) function returns requestId successfully
        // it will then call fulfillRandomness() automatically. So basically we request chainlink
        // for a random number and in the run time chainlink generates random number and send
        // via fulfillRandomness() function.
        bytes32 requestId = requestRandomness(keyhash, fee);
        // emit RequestedRandomness(requestId);
    }

    function fulfillRandomness(bytes32 _requestId, uint256 _randomness)
        internal
        override
    {
        require(
            lottery_state == LOTTERY_STATE.CALCULATING_WINNER,
            "You are not there yet!"
        );

        require(_randomness > 0, "Random-Not-Found");

        uint256 indexOfWinner = _randomness % players.length;
        recentWinner = players[indexOfWinner];

        // transfer amount to winner
        recentWinner.transfer(address(this).balance);

        // Reset all variables
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
    }
}
