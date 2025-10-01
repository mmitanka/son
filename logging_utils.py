import logging
import os

def setup_simulation_logging(log_filename):
    if not os.path.exists("logs"):
        os.makedirs("logs")

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f"logs/{log_filename}", mode="w", encoding="utf-8")
        ]
    )