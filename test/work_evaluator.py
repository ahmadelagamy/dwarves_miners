import logging
import asyncio
from typing import Dict, Any

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

logger = logging.getLogger(__name__)

class WorkEvaluator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.create_model().to(self.device)
        self.loss_fn = nn.MSELoss()
        self.eval_data = self.load_eval_data()
        self.batch_size = config.get('eval_batch_size', 64)
        self.num_workers = config.get('eval_num_workers', 4)
        self.eval_loader = DataLoader(
            self.eval_data,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=True
        )

    def create_model(self) -> nn.Module:
        """Create the model architecture."""
        # This is a placeholder. Replace with your actual model architecture.
        return nn.Sequential(
            nn.Linear(10, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )

    def load_eval_data(self) -> TensorDataset:
        """Load the evaluation dataset."""
        # This is a placeholder. Replace with your actual data loading logic.
        x = torch.randn(10000, 10)
        y = torch.randn(10000, 1)
        return TensorDataset(x, y)

    async def evaluate(self, model_state_dict: Dict[str, torch.Tensor]) -> float:
        """Evaluate the submitted model."""
        try:
            # Load the submitted state dict
            self.model.load_state_dict(model_state_dict)
            self.model.eval()

            total_loss = 0.0
            total_samples = 0

            with torch.no_grad():
                for batch in self.eval_loader:
                    inputs, targets = batch
                    inputs = inputs.to(self.device)
                    targets = targets.to(self.device)

                    outputs = self.model(inputs)
                    loss = self.loss_fn(outputs, targets)

                    total_loss += loss.item() * inputs.size(0)
                    total_samples += inputs.size(0)

            avg_loss = total_loss / total_samples
            logger.info(f"Evaluation completed. Average loss: {avg_loss}")
            return avg_loss

        except Exception as e:
            logger.error(f"Error during work evaluation: {e}")
            raise

    async def evaluate_with_timeout(self, model_state_dict: Dict[str, torch.Tensor], timeout: float = 30.0) -> float:
        """Evaluate the submitted model with a timeout."""
        try:
            return await asyncio.wait_for(self.evaluate(model_state_dict), timeout)
        except asyncio.TimeoutError:
            logger.error("Evaluation timed out")
            raise
        except Exception as e:
            logger.error(f"Error during work evaluation: {e}")
            raise

    def update_eval_data(self, new_data: TensorDataset):
        """Update the evaluation dataset."""
        self.eval_data = new_data
        self.eval_loader = DataLoader(
            self.eval_data,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=True
        )
        logger.info("Evaluation dataset updated")