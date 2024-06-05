import torch


def get_device() -> torch.device:
    # If there's a GPU available...
    if torch.cuda.is_available():
        # Tell PyTorch to use the GPU.
        device = torch.device("cuda:1")
        print(f"There are {torch.cuda.device_count()} GPU(s) available.")
        print(f"We will use the GPU: {torch.cuda.get_device_name(0)}")
    # If not...
    else:
        print("No GPU available, using the CPU instead.")
        device = torch.device("cpu")

    return device
