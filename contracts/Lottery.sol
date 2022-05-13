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

contract Lottery is Ownable {
    // safe math library check uint256 for integer overflows
    using SafeMathChainlink for uint256;

    address payable[] public players;
    uint256 public usdEntryFee;

    AggregatorV3Interface internal ethUsdPriceFeed;

    // 0 -> OPEN, 1-> CLOSED, 2-> CALCULATING_WINNER
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lottery_state;

    constructor(address _priceFeedAddress) public {
        usdEntryFee = 50 * (10**18);
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        lottery_state = LOTTERY_STATE.CLOSED; // OR lottery_state = 1;
    }

    function enter() public payable {
        require(
            lottery_state == LOTTERY_STATE.OPEN,
            "Sorry the Lottery is inactive now!!"
        );
        // minimum usdEntryFee required to become player
        require(msg.value >= getEntranceFee(), "Not enough ETH!!");
        players.push(msg.sender);
    }

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

    function endLottery() public {}
}
