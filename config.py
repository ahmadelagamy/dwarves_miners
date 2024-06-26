import os
from typing import Dict, Any
import yaml
import bittensor as bt

def load_config() -> Dict[str, Any]:
    """Load configuration from YAML file and environment variables."""
    # Load from YAML file
    config_path = os.getenv('MINING_POOL_CONFIG', 'config.yaml')
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    # Override with environment variables
    for key in config:
        env_var = f'MINING_POOL_{key.upper()}'
        if os.getenv(env_var):
            config[key] = os.getenv(env_var)

    # Load Bittensor-specific configuration
    bt_config = bt.config(bt.Config())
    bt_config.neuron.name = config.get('neuron_name', 'mining_pool')
    bt_config.wallet.name = config.get('wallet_name', 'mining_pool_wallet')
    bt_config.wallet.hotkey = config.get('wallet_hotkey', 'mining_pool_hotkey')

    config['bittensor'] = bt_config

    return config