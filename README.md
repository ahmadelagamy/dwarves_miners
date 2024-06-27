# Bittensor Mining Pool

This project implements a mining pool for the Bittensor network, allowing miners to collaborate and share rewards.

## Components

1. **Main Application (`main.py`)**: The entry point of the application, handling startup and shutdown.

2. **Configuration (`config.py`)**: Manages loading and parsing of configuration from YAML and environment variables.

3. **Pool Manager (`pool_manager.py`)**: Coordinates all mining pool operations, including miner registration, work submission, and reward distribution.

4. **Miner Manager (`miner_manager.py`)**: Handles miner registration and performance tracking.

5. **Work Evaluator (`work_evaluator.py`)**: Evaluates the work submitted by miners.

6. **Reward Distributor (`reward_distributor.py`)**: Calculates and distributes rewards to miners based on their contributions.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:
2. Create a virtual environment (optional but recommended):
3. Install the required packages:

## Configuration

1. Copy the example configuration file:
2. Edit `config.yaml` to set your desired configuration:
```yaml
neuron_name: mining_pool
wallet_name: mining_pool_wallet
wallet_hotkey: mining_pool_hotkey
reward_interval: 3600
total_reward: 10
log_level: INFO
network: test
chain_endpoint: wss://test.finney.opentensor.ai:443
netuid: 1

Running the Mining Pool

Ensure your Bittensor wallet is set up and has sufficient funds for registration and operations.
Start the mining pool:
Copypython main.py

The application will start and log its progress. You can monitor the log file (mining_pool.log) for detailed information.

Development and Extending the Pool

To modify the miner registration process, edit the MinerManager class in miner_manager.py.
To change how work is evaluated, update the WorkEvaluator class in work_evaluator.py.
To adjust the reward distribution algorithm, modify the RewardDistributor class in reward_distributor.py.

Troubleshooting

If you encounter connection issues, ensure your chain_endpoint in the configuration is correct and accessible.
For registration problems, check that your wallet has sufficient funds and that you're using the correct netuid.
Review the log file for detailed error messages and stack traces.

Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
