import unittest
from unittest.mock import Mock, patch
from pool_manager import PoolManager, AxonSetupError, NeuronRegistrationError
import bittensor as bt

class TestPoolManager(unittest.TestCase):
    def setUp(self):
        # Create a mock configuration
        mock_bt_config = Mock()
        mock_bt_config.wallet = Mock()
        mock_bt_config.wallet.name = 'test_wallet'
        mock_bt_config.wallet.hotkey = 'test_hotkey'
        mock_bt_config.netuid = 1

        self.mock_config = {
            'bittensor': mock_bt_config,
            'subtensor': Mock(),
            'reward_interval': 3600,
            'netuid': 1,
            'db_file': ':memory:'  # Use in-memory SQLite for testing
        }
        
        # Patch bittensor.wallet and bittensor.subtensor to return mocks
        with patch('bittensor.wallet') as mock_wallet, \
             patch('bittensor.subtensor') as mock_subtensor:
            mock_wallet.return_value = Mock()
            mock_subtensor.return_value = Mock()
            mock_subtensor.return_value.metagraph.return_value = Mock()
            self.pool_manager = PoolManager(self.mock_config)

    @patch('bittensor.axon')
    def test_setup_axon(self, mock_axon):
        # Reset the axon attribute
        self.pool_manager.axon = None
        
        # Call setup_axon
        self.pool_manager.setup_axon()
        
        # Assert that bt.axon was called
        mock_axon.assert_called_once()
        
        # Assert that axon is not None after setup
        self.assertIsNotNone(self.pool_manager.axon)

    @patch('bittensor.subtensor')
    async def test_register_neuron_success(self, mock_subtensor):
        # Mock the behavior of subtensor
        mock_subtensor.return_value.is_neuron_registered.return_value = False
        mock_subtensor.return_value.register.return_value = True
        
        # Call register_neuron
        await self.pool_manager.register_neuron()
        
        # Assert that register was called
        mock_subtensor.return_value.register.assert_called_once()

    @patch('bittensor.subtensor')
    async def test_register_neuron_failure(self, mock_subtensor):
        # Mock the behavior of subtensor
        mock_subtensor.return_value.is_neuron_registered.return_value = False
        mock_subtensor.return_value.register.return_value = False
        
        # Assert that NeuronRegistrationError is raised
        with self.assertRaises(NeuronRegistrationError):
            await self.pool_manager.register_neuron()

if __name__ == '__main__':
    unittest.main()