from database import Database


class MinerManager:
    def __init__(self, db_file):
        self.db = Database(db_file)

    async def register_miner(self, miner_hotkey):
        self.db.register_miner(miner_hotkey)
        return True

    async def update_miner_performance(self, miner_hotkey, performance):
        import time
        self.db.update_miner_performance(miner_hotkey, performance, int(time.time()))

    def get_miner_performances(self):
        return self.db.get_miner_performances()