import bittensor as bt
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Bittensor version: {bt.__version__}")

try:
    config = bt.config()
    logger.info(f"Config initialized: {config}")
    logger.info(f"Neuron name: {config.neuron.name}")
except Exception as e:
    logger.exception(f"Error initializing Bittensor config: {e}")

try:
    subtensor = bt.subtensor()
    logger.info(f"Subtensor initialized: {subtensor}")
except Exception as e:
    logger.exception(f"Error initializing Subtensor: {e}")