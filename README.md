# Dwarves

## Overview

This project implements a mining pool manager for a cryptocurrency network. It includes functionalities for distributing rewards to miners, handling miner registration, and processing work submissions. The system is designed to operate asynchronously to efficiently manage network interactions and reward distributions.

## Features

- **Reward Distribution**: Periodically distributes rewards to miners based on their performance.
- **Miner Registration**: Handles registration requests from miners, allowing them to join the mining pool.
- **Work Submission**: Processes work submissions from miners, which is essential for validating mining efforts and distributing rewards accordingly.

## Technical Details

### Technologies Used

- Python 3.x
- asyncio for asynchronous programming

### Key Components

- [`pool_manager.py`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Froot%2Fprojects%2Fdwarves%2Fpool_manager.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%5D "/root/projects/dwarves/pool_manager.py"): Contains the core logic for managing the mining pool, including reward distribution, miner registration, and work submission handling.

#### [`_reward_loop`](command:_github.copilot.openSymbolFromReferences?%5B%7B%22%24mid%22%3A1%2C%22path%22%3A%22%2Froot%2Fprojects%2Fdwarves%2Fpool_manager.py%22%2C%22scheme%22%3A%22file%22%7D%2C%7B%22line%22%3A75%2C%22character%22%3A14%7D%5D "pool_manager.py")

- Periodically distributes rewards to miners.
- Utilizes [`asyncio.sleep`](command:_github.copilot.openSymbolFromReferences?%5B%7B%22%24mid%22%3A1%2C%22path%22%3A%22%2Fusr%2Flib%2Fpython3.10%2Fasyncio%2F__init__.py%22%2C%22scheme%22%3A%22file%22%7D%2C%7B%22line%22%3A0%2C%22character%22%3A0%7D%5D "../../../usr/lib/python3.10/asyncio/__init__.py") for scheduling reward distribution based on a predefined interval.
- Gathers miner performances via [`miner_manager.get_miner_performances()`](command:_github.copilot.openSymbolFromReferences?%5B%7B%22%24mid%22%3A1%2C%22path%22%3A%22%2Froot%2Fprojects%2Fdwarves%2Fpool_manager.py%22%2C%22scheme%22%3A%22file%22%7D%2C%7B%22line%22%3A17%2C%22character%22%3A13%7D%5D "pool_manager.py").
- Distributes rewards through [`reward_distributor.distribute()`](command:_github.copilot.openSymbolFromReferences?%5B%7B%22%24mid%22%3A1%2C%22path%22%3A%22%2Froot%2Fprojects%2Fdwarves%2Fpool_manager.py%22%2C%22scheme%22%3A%22file%22%7D%2C%7B%22line%22%3A19%2C%22character%22%3A13%7D%5D "pool_manager.py").

#### [`handle_registration`](command:_github.copilot.openSymbolFromReferences?%5B%7B%22%24mid%22%3A1%2C%22path%22%3A%22%2Froot%2Fprojects%2Fdwarves%2Fpool_manager.py%22%2C%22scheme%22%3A%22file%22%7D%2C%7B%22line%22%3A85%2C%22character%22%3A14%7D%5D "pool_manager.py")

- Handles registration requests from miners.
- Extracts miner's hotkey from the [`synapse`](command:_github.copilot.openSymbolFromReferences?%5B%7B%22%24mid%22%3A1%2C%22path%22%3A%22%2Froot%2Fprojects%2Fdwarves%2Fpool_manager.py%22%2C%22scheme%22%3A%22file%22%7D%2C%7B%22line%22%3A85%2C%22character%22%3A40%7D%5D "pool_manager.py") object.
- Registers the miner using [`miner_manager.register_miner()`](command:_github.copilot.openSymbolFromReferences?%5B%7B%22%24mid%22%3A1%2C%22path%22%3A%22%2Froot%2Fprojects%2Fdwarves%2Fpool_manager.py%22%2C%22scheme%22%3A%22file%22%7D%2C%7B%22line%22%3A17%2C%22character%22%3A13%7D%5D "pool_manager.py").
- Sets [`registration_success`](command:_github.copilot.openSymbolFromReferences?%5B%7B%22%24mid%22%3A1%2C%22path%22%3A%22%2Froot%2Fprojects%2Fdwarves%2Fdwarves%2Flib%2Fpython3.10%2Fsite-packages%2Fbittensor%2Fsynapse.py%22%2C%22scheme%22%3A%22file%22%7D%2C%7B%22line%22%3A491%2C%22character%22%3A8%7D%5D "dwarves/lib/python3.10/site-packages/bittensor/synapse.py") in the [`synapse`](command:_github.copilot.openSymbolFromReferences?%5B%7B%22%24mid%22%3A1%2C%22path%22%3A%22%2Froot%2Fprojects%2Fdwarves%2Fpool_manager.py%22%2C%22scheme%22%3A%22file%22%7D%2C%7B%22line%22%3A85%2C%22character%22%3A40%7D%5D "pool_manager.py") object based on the registration outcome.

#### [`handle_work_submission`](command:_github.copilot.openSymbolFromReferences?%5B%7B%22%24mid%22%3A1%2C%22path%22%3A%22%2Froot%2Fprojects%2Fdwarves%2Fpool_manager.py%22%2C%22scheme%22%3A%22file%22%7D%2C%7B%22line%22%3A97%2C%22character%22%3A14%7D%5D "pool_manager.py")

- Stub for handling work submissions from miners. (Implementation details not provided in the excerpt.)

## Getting Started

To get started with this project, ensure you have Python 3.x installed on your system. Clone the repository and install the required dependencies.

```bash
git clone <repository-url>
cd <project-directory>
pip install -r requirements.txt
```

To run the pool manager, execute:

```bash
python pool_manager.py
```

## Contributing

Contributions to the project are welcome. Please follow the standard fork-and-pull request workflow. Ensure you write tests for new features and run existing tests to confirm your changes do not break existing functionalities.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
