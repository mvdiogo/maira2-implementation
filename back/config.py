from os import getenv, cpu_count
from dotenv import load_dotenv
import torch

load_dotenv()


class Config:
    """Configuration settings for the MAIRA Report Generator."""

    def __init__(self):
        self.hf_token = getenv("HF_TOKEN")
        if not self.hf_token:
            raise ValueError("HF_TOKEN environment variable not set.")
        self.model_name = "microsoft/maira-2"
        self.results_dir = "results"
        self.num_threads = self.configure_threads()

    @staticmethod
    def configure_threads() -> int:
        """
        Configure CPU threads based on available cores if CUDA is not available.
        """
        if not torch.cuda.is_available():
            num_threads = int(getenv("NUM_THREADS", cpu_count()/2 or 1))
            torch.set_num_threads(num_threads)
            print(f"Using {num_threads} CPU threads.")
            return num_threads
        return 0


config = Config()
