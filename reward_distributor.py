import logging
from typing import Dict, Any
import asyncio
import bittensor as bt

logger = logging.getLogger(__name__)

class RewardDistributor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.total_reward = config.get('total_reward', 1000)
        self.reward_interval = config.get('reward_interval', 3600)  # Default to 1 hour
        self.min_payout = config.get('min_payout', 0.1)  # Minimum payout threshold
        self.wallet = bt.wallet(config=config['bittensor'])
        self.subtensor = bt.subtensor(config=config['bittensor'])

    async def distribute(self, miner_performances: Dict[str, float]):
        """Calculate and distribute rewards to miners."""
        try:
            total_inverse_loss = sum(1 / loss for loss in miner_performances.values() if loss != float('inf'))
            
            if total_inverse_loss == 0:
                logger.warning("No valid performances to reward")
                return

            rewards = {}
            for miner_hotkey, loss in miner_performances.items():
                if loss == float('inf'):
                    continue
                reward = (1 / loss / total_inverse_loss) * self.total_reward
                if reward >= self.min_payout:
                    rewards[miner_hotkey] = reward
                else:
                    logger.info(f"Miner {miner_hotkey} reward {reward} below minimum payout threshold")

            await self._send_rewards(rewards)

        except Exception as e:
            logger.error(f"Error during reward distribution: {e}")
            raise

    async def _send_rewards(self, rewards: Dict[str, float]):
        """Send rewards to miners using Bittensor's transfer mechanism."""
        for miner_hotkey, reward in rewards.items():
            try:
                # Convert reward to RAO (Bittensor's smallest unit)
                reward_rao = int(reward * 1e9)
                
                # Perform the transfer
                success = await self.subtensor.transfer(
                    wallet=self.wallet,
                    dest=miner_hotkey,
                    amount=reward_rao,
                    wait_for_inclusion=True,
                    prompt=False
                )

                if success:
                    logger.info(f"Successfully sent {reward} TAO to miner {miner_hotkey}")
                else:
                    logger.error(f"Failed to send {reward} TAO to miner {miner_hotkey}")

            except Exception as e:
                logger.error(f"Error sending reward to miner {miner_hotkey}: {e}")

    async def run(self, get_miner_performances):
        """Run the reward distribution loop."""
        while True:
            await asyncio.sleep(self.reward_interval)
            try:
                miner_performances = await get_miner_performances()
                await self.distribute(miner_performances)
            except Exception as e:
                logger.error(f"Error in reward distribution cycle: {e}")

    def update_total_reward(self, new_total_reward: float):
        """Update the total reward amount."""
        self.total_reward = new_total_reward
        logger.info(f"Total reward updated to {self.total_reward}")

    def update_reward_interval(self, new_interval: int):
        """Update the reward distribution interval."""
        self.reward_interval = new_interval
        logger.info(f"Reward interval updated to {self.reward_interval} seconds")