import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RewardDistributor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.total_reward = config['total_reward']
        self.reward_interval = config['reward_interval']
        self.min_payout = config.get('min_payout', 0.1)  # Minimum payout threshold

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
        # Implement the actual reward distribution logic here
        for miner_hotkey, reward in rewards.items():
            logger.info(f"Would send {reward} TAO to miner {miner_hotkey}")

    def update_total_reward(self, new_total_reward: float):
        """Update the total reward amount."""
        self.total_reward = new_total_reward
        logger.info(f"Total reward updated to {self.total_reward}")

    def update_reward_interval(self, new_interval: int):
        """Update the reward distribution interval."""
        self.reward_interval = new_interval
        logger.info(f"Reward interval updated to {self.reward_interval} seconds")