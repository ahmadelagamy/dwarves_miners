import asyncio
import logging
from typing import Dict, Any

import bittensor as bt
from miner_manager import MinerManager
from work_evaluator import WorkEvaluator
from reward_distributor import RewardDistributor

logger = logging.getLogger(__name__)

class PoolManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.bt_config = config['bittensor']
        self.wallet = bt.wallet(config=self.bt_config)
        self.subtensor = bt.subtensor(config=self.bt_config)
        self.miner_manager = MinerManager()
        self.work_evaluator = WorkEvaluator(config)
        self.reward_distributor = RewardDistributor(config['total_reward'])
        self.axon = None
        self.is_running = False
        self.reward_interval = config['reward_interval']
        self.reward_distributor = RewardDistributor(config)

    async def start(self):
        """Start the pool manager and its components."""
        logger.info("Starting Pool Manager...")
        try:
            await self._setup_axon()
            await self._register_neuron()
            self.is_running = True
            asyncio.create_task(self.reward_distributor.run(self.miner_manager.get_miner_performances))
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
            await self.axon.stop()
        logger.info("Pool Manager stopped.")

    async def _setup_axon(self):
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
        await self.axon.start()
        logger.info(f"Axon server started on port {self.axon.port}")

    async def _register_neuron(self):
        """Register the mining pool neuron on the Bittensor network."""
        if not self.subtensor.is_registered(self.wallet.hotkey.ss58_address):
            logger.info("Registering mining pool neuron...")
            success = await self.subtensor.register(wallet=self.wallet, prompt=False)
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
            model_state_dict = synapse.work
            loss = await self.work_evaluator.evaluate_with_timeout(model_state_dict)
            await self.miner_manager.update_miner_performance(miner_hotkey, loss)
            synapse.loss = loss
            logger.info(f"Work submission processed for {miner_hotkey} with loss {loss}")
        except asyncio.TimeoutError:
            logger.warning(f"Work submission evaluation timed out for {synapse.dendrite.hotkey}")
            synapse.loss = None
        except Exception as e:
            logger.error(f"Error handling work submission for {synapse.dendrite.hotkey}: {e}")
            synapse.loss = None
        return synapse
    def blacklist_check(self, synapse: bt.Synapse) -> bool:
        """Check if a request should be blacklisted."""
        # Implement your blacklist logic here
        return False

    def prioritize(self, synapse: bt.Synapse) -> float:
        """Prioritize incoming requests."""
        # Implement your prioritization logic here
        return 1.0