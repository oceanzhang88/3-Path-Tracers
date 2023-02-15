import time
from collections import defaultdict
from logging import Logger


class SimpleProfiler:
    """A simple tool for measuring how much time each portion of rendering is taking"""

    def __init__(self) -> None:
        self.start_time = {}
        self.results = defaultdict(lambda: 0)

    def log_start(self, key):
        self.start_time[key] = time.time()

    def log_end(self, key):
        self.results[key] += time.time() - self.start_time[key]

    def clear(self):
        self.start_time.clear()
        self.results.clear()

    def log_results(self, message: str, logger: Logger):
        length = max([len(key) for key in self.results.keys()])
        text = [message, *(f"{k:<{length}} {v*1000:.2f}ms" for k, v in self.results.items())]
        logger.info("\n".join(text))
