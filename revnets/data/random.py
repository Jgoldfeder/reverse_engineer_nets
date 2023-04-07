from dataclasses import dataclass

import cli
import torch
from torch.utils.data import TensorDataset

from ..utils import config
from . import output_supervision
from .base import Split


@dataclass
class Dataset(output_supervision.Dataset):
    num_samples: int = config.sampling_data_size

    def __post_init__(self):
        super().__post_init__()
        self.train_val_dataset: TensorDataset | None = None
        self.train_dataset: TensorDataset | None = None
        self.val_dataset: TensorDataset | None = None
        self.test_dataset: TensorDataset | None = None
        self.batch_size = config.reconstruction_batch_size

    @property
    def input_shape(self):
        train_sample = self.original_dataset.train_val_dataset[0]
        return train_sample[0].shape

    def get_dataset_shape(self, split: Split):
        num_samples = (
            self.num_samples
            if split == Split.train_val
            else int(self.num_samples * self.validation_ratio)
        )
        if split == Split.train_val:
            assert (
                num_samples > 0
            ), f"Number of {split.value} samples must be greater than 0"
        return num_samples, *self.input_shape

    @classmethod
    def generate_random_inputs(cls, shape):
        dtype = torch.float64 if config.precision == 64 else torch.float32
        # same mean and std as training data
        return torch.randn(shape, dtype=dtype)

    def generate_dataset(self, split: Split):
        dataset_shape = self.get_dataset_shape(split)
        inputs = self.generate_random_inputs(dataset_shape)
        return self.construct_dataset(inputs, split)

    def get_targets(self, inputs):
        inputs_dataset = TensorDataset(inputs)
        batch_size = self.original_dataset.eval_batch_size
        dataloader = torch.utils.data.DataLoader(inputs_dataset, batch_size=batch_size)
        return self.get_output_targets(dataloader)

    def construct_dataset(self, inputs, split: Split = None):
        n = len(inputs)
        split_message = f"{split.value} " if split is not None else ""
        message = f"Generating {split_message}dataset with {n} random inputs.."
        with cli.status(message):
            targets = self.get_targets(inputs)
        return TensorDataset(inputs, targets)
