import asyncio
import signal
import sys
import logging
from typing import NoReturn

import bittensor as bt
from pool_manager import PoolManager
from config import load_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mining_pool.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MiningPoolApp:
    def __init__(self):
        self.config = load_config()
        self.pool_manager = PoolManager(self.config)
        self.shutdown_event = asyncio.Event()

    async def start(self) -> NoReturn:
        """Start the mining pool application."""
        logger.info("Starting Bittensor Mining Pool...")
        
        try:
            # Register signal handlers
            for sig in (signal.SIGINT, signal.SIGTERM):
                asyncio.get_running_loop().add_signal_handler(
                    sig, lambda s=sig: asyncio.create_task(self.shutdown(s))
                )
            
            # Start the pool manager
            await self.pool_manager.start()
            
            # Run until shutdown is called
            await self.shutdown_event.wait()
            
        except Exception as e:
            logger.exception(f"Unexpected error occurred: {e}")
        finally:
            await self.cleanup()

    async def shutdown(self, sig: signal.Signals) -> None:
        """Shutdown the application gracefully."""
        logger.info(f"Received exit signal {sig.name}...")
        self.shutdown_event.set()

    async def cleanup(self) -> None:
        """Perform cleanup operations."""
        logger.info("Cleaning up...")
        await self.pool_manager.stop()
        logger.info("Shutdown complete.")

async def main() -> NoReturn:
    """Main entry point of the application."""
    app = MiningPoolApp()
    await app.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)