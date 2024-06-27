import bittensor as bt
from miner_manager import MinerManager
from work_evaluator import WorkEvaluator
from reward_distributor import RewardDistributor
import asyncio
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class PoolManager:
    """Manages the mining pool and its components.

    The PoolManager class is responsible for starting and stopping the mining pool,
    setting up the axon server, registering the mining pool neuron on the Bittensor network,
    and distributing rewards to miners.

    Attributes:
        config (dict): The configuration settings for the mining pool.
        bt_config (dict): The Bittensor configuration settings.
        wallet (bt.wallet): The Bittensor wallet used for registration and reward distribution.
        subtensor (subtensor.Subtensor): The Bittensor Subtensor instance for interacting with the network.
        miner_manager (MinerManager): The manager for handling miner registration and performance tracking.
        work_evaluator (WorkEvaluator): The evaluator for processing work submissions from miners.
        reward_distributor (RewardDistributor): The distributor for distributing rewards to miners.
        axon (bt.axon): The axon server for handling incoming requests.
        is_running (bool): Flag indicating whether the pool manager is running.
        reward_interval (int): The interval (in seconds) for distributing rewards to miners.

    """

    def __init__(self, config):
        self.config = config
        self.bt_config = config['bittensor']
        self.wallet = bt.wallet(config=self.bt_config)
        self.subtensor = config['subtensor']
        self.miner_manager = MinerManager()
        self.work_evaluator = WorkEvaluator(config)
        self.reward_distributor = RewardDistributor(config)
        self.axon = None
        self.is_running = False
        self.reward_interval = config['reward_interval']

    async def start(self):
        """Start the pool manager and its components."""
        logger.info("Starting Pool Manager...")
        try:
            self._setup_axon()
            await self._register_neuron()
            self.is_running = True
            asyncio.create_task(self._reward_loop())
            logger.info("Pool Manager started successfully.")
        except Exception as e:
            logger.exception(f"Failed to start Pool Manager: {e}")
            await self.stop()

    async def stop(self):
        """Stop the pool manager and its components."""
        logger.info("Stopping Pool Manager...")
        self.is_running = False
        if self.axon:
            self.axon.stop()
        logger.info("Pool Manager stopped.")

    def _setup_axon(self):
        """Set up the axon server."""
        self.axon = bt.axon(wallet=self.wallet)
        self.axon.attach(
            forward_fn=self.handle_registration,
            blacklist_fn=self.blacklist_check,
            priority_fn=self.prioritize
        )
        self.axon.attach(
            forward_fn=self.handle_work_submission,
            blacklist_fn=self.blacklist_check,
            priority_fn=self.prioritize
        )
        self.axon.start()
        logger.info(f"Axon server started on port {self.axon.port}")

    async def _register_neuron(self):
        """Register the mining pool neuron on the Bittensor network."""
        neuron = self.subtensor.get_neuron_for_pubkey_and_subnet(
            self.wallet.hotkey.ss58_address, 
            self.config.get('netuid', 1)  # Use the appropriate netuid
        )
        if neuron is None:
            logger.info("Registering mining pool neuron...")
            success = await self.subtensor.register(
                wallet=self.wallet,
                prompt=False,
                netuid=self.config.get('netuid', 1)  # Use the appropriate netuid
            )
            if success:
                logger.info(f"Mining pool neuron registered with hotkey: {self.wallet.hotkey.ss58_address}")
            else:
                raise Exception("Failed to register mining pool neuron")
        else:
            logger.info(f"Mining pool neuron already registered with hotkey: {self.wallet.hotkey.ss58_address}")


    async def _reward_loop(self):
        """Periodically distribute rewards to miners."""
        while self.is_running:
            try:
                await asyncio.sleep(self.reward_interval)
                miner_performances = self.miner_manager.get_miner_performances()
                await self.reward_distributor.distribute(miner_performances)
            except Exception as e:
                logger.error(f"Error in reward distribution: {e}")

    async def handle_registration(self, synapse: bt.Synapse) -> bt.Synapse:
        """Handle miner registration requests."""
        try:
            miner_hotkey = synapse.dendrite.hotkey
            success = await self.miner_manager.register_miner(miner_hotkey)
            synapse.registration_success = success
            logger.info(f"Miner registration {'successful' if success else 'failed'} for {miner_hotkey}")
        except Exception as e:
            logger.error(f"Error handling registration for {synapse.dendrite.hotkey}: {e}")
            synapse.registration_success = False
        return synapse

    async def handle_work_submission(self, synapse: bt.Synapse) -> bt.Synapse:
        """Handle work submissions from miners."""
        try:
            miner_hotkey = synapse.dendrite.hotkey
            work = synapse.work
            loss = await self.work_evaluator.evaluate(work)
            await self.miner_manager.update_miner_performance(miner_hotkey, loss)
            synapse.loss = loss
            logger.info(f"Work submission processed for {miner_hotkey} with loss {loss}")
        except Exception as e:
            logger.error(f"Error handling work submission for {synapse.dendrite.hotkey}: {e}")
            synapse.loss = None
        return synapse

    def blacklist_check(self, synapse: bt.Synapse) -> Tuple[bool, str]:
        """Check if a request should be blacklisted."""
        # Implement your blacklist logic here
        return False, "Not blacklisted"

    def prioritize(self, synapse: bt.Synapse) -> float:
        """Prioritize incoming requests."""
        # Implement your prioritization logic here
        return 1.0