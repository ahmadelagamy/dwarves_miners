import asyncio
import logging
import time
from typing import Dict, Any
import aiosqlite
import json

logger = logging.getLogger(__name__)

class MinerManager:
    def __init__(self, db_path: str = 'miners.db'):
        self.db_path = db_path
        self.lock = asyncio.Lock()
        self.miners_cache = {}

    async def initialize(self):
        """Initialize the database and load miners into cache."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS miners (
                    hotkey TEXT PRIMARY KEY,
                    best_loss REAL,
                    last_submission INTEGER,
                    metadata TEXT
                )
            ''')
            await db.commit()

        await self._load_miners_to_cache()

    async def _load_miners_to_cache(self):
        """Load all miners from the database into the cache."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT * FROM miners') as cursor:
                async for row in cursor:
                    self.miners_cache[row[0]] = {
                        'best_loss': row[1],
                        'last_submission': row[2],
                        'metadata': json.loads(row[3])
                    }

    async def register_miner(self, miner_hotkey: str) -> bool:
        """Register a new miner."""
        async with self.lock:
            if miner_hotkey in self.miners_cache:
                logger.info(f"Miner {miner_hotkey} already registered")
                return False

            try:
                async with aiosqlite.connect(self.db_path) as db:
                    await db.execute('''
                        INSERT INTO miners (hotkey, best_loss, last_submission, metadata)
                        VALUES (?, ?, ?, ?)
                    ''', (miner_hotkey, float('inf'), 0, '{}'))
                    await db.commit()

                self.miners_cache[miner_hotkey] = {
                    'best_loss': float('inf'),
                    'last_submission': 0,
                    'metadata': {}
                }
                logger.info(f"Miner {miner_hotkey} registered successfully")
                return True
            except Exception as e:
                logger.error(f"Error registering miner {miner_hotkey}: {e}")
                return False

    async def update_miner_performance(self, miner_hotkey: str, loss: float):
        """Update a miner's performance."""
        async with self.lock:
            if miner_hotkey not in self.miners_cache:
                logger.warning(f"Attempt to update non-existent miner {miner_hotkey}")
                return

            try:
                current_time = int(time.time())
                if loss < self.miners_cache[miner_hotkey]['best_loss']:
                    self.miners_cache[miner_hotkey]['best_loss'] = loss

                self.miners_cache[miner_hotkey]['last_submission'] = current_time

                async with aiosqlite.connect(self.db_path) as db:
                    await db.execute('''
                        UPDATE miners 
                        SET best_loss = ?, last_submission = ?
                        WHERE hotkey = ?
                    ''', (loss, current_time, miner_hotkey))
                    await db.commit()

                logger.info(f"Updated performance for miner {miner_hotkey}: loss = {loss}")
            except Exception as e:
                logger.error(f"Error updating miner {miner_hotkey} performance: {e}")

    async def get_miner_performances(self) -> Dict[str, float]:
        """Get the best performance of all miners."""
        async with self.lock:
            return {hotkey: data['best_loss'] for hotkey, data in self.miners_cache.items()}

    async def get_miner_details(self, miner_hotkey: str) -> Dict[str, Any]:
        """Get detailed information about a specific miner."""
        async with self.lock:
            if miner_hotkey not in self.miners_cache:
                logger.warning(f"Attempt to get details of non-existent miner {miner_hotkey}")
                return None
            return self.miners_cache[miner_hotkey]

    async def update_miner_metadata(self, miner_hotkey: str, metadata: Dict[str, Any]):
        """Update a miner's metadata."""
        async with self.lock:
            if miner_hotkey not in self.miners_cache:
                logger.warning(f"Attempt to update metadata of non-existent miner {miner_hotkey}")
                return

            try:
                self.miners_cache[miner_hotkey]['metadata'].update(metadata)
                metadata_json = json.dumps(self.miners_cache[miner_hotkey]['metadata'])

                async with aiosqlite.connect(self.db_path) as db:
                    await db.execute('''
                        UPDATE miners 
                        SET metadata = ?
                        WHERE hotkey = ?
                    ''', (metadata_json, miner_hotkey))
                    await db.commit()

                logger.info(f"Updated metadata for miner {miner_hotkey}")
            except Exception as e:
                logger.error(f"Error updating metadata for miner {miner_hotkey}: {e}")

    async def remove_miner(self, miner_hotkey: str) -> bool:
        """Remove a miner from the pool."""
        async with self.lock:
            if miner_hotkey not in self.miners_cache:
                logger.warning(f"Attempt to remove non-existent miner {miner_hotkey}")
                return False

            try:
                del self.miners_cache[miner_hotkey]

                async with aiosqlite.connect(self.db_path) as db:
                    await db.execute('DELETE FROM miners WHERE hotkey = ?', (miner_hotkey,))
                    await db.commit()

                logger.info(f"Miner {miner_hotkey} removed successfully")
                return True
            except Exception as e:
                logger.error(f"Error removing miner {miner_hotkey}: {e}")
                return False