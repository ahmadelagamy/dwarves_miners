import os
from typing import Dict, Any
import yaml
import bittensor as bt
import logging
from munch import Munch

logger = logging.getLogger(__name__)

def load_config() -> Dict[str, Any]:
    """Load configuration from YAML file and environment variables."""
    try:
        # Load from YAML file
        config_path = os.getenv('MINING_POOL_CONFIG', 'config.yaml')
        logger.info(f"Attempting to load config from: {config_path}")
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        logger.info(f"Loaded config from YAML: {config}")

        # Override with environment variables
        for key in config:
            env_var = f'MINING_POOL_{key.upper()}'
            if os.getenv(env_var):
                config[key] = os.getenv(env_var)
                logger.info(f"Overridden {key} with environment variable")

        # Initialize Bittensor configuration
        logger.info("Initializing Bittensor configuration")
        bt_config = Munch()
        bt_config.neuron = Munch()
        bt_config.wallet = Munch()
        bt_config.subtensor = Munch()

        bt_config.neuron.name = config.get('neuron_name', 'mining_pool')
        bt_config.wallet.name = config.get('wallet_name', 'mining_pool_wallet')
        bt_config.wallet.hotkey = config.get('wallet_hotkey', 'mining_pool_hotkey')
        bt_config.subtensor.network = config.get('network', 'test')
        bt_config.subtensor.chain_endpoint = config.get('chain_endpoint', 'wss://test.finney.opentensor.ai:443')
        bt_config.subtensor.netuid= 100
        config['bittensor'] = bt_config
        logger.info("Bittensor configuration initialized successfully")

        # Initialize subtensor
        subtensor = bt.subtensor(
            network=bt_config.subtensor.network
        )
        config['subtensor'] = subtensor

        return config
    except Exception as e:
        logger.exception(f"Error in load_config: {e}")
        raise