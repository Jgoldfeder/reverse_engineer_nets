from __future__ import annotations

import typing

import pytorch_lightning as pl
import torch.nn
from cacher import decorator
from cacher.caches import base

from .config import config

if typing.TYPE_CHECKING:
    from revnets.networks.models.trainable import Model  # noqa: autoimport


class TuneModel(pl.LightningModule):
    def __init__(self, model, data):
        super().__init__()
        self.model: Model = model
        self.data = data
        self.batch_size = 1
        self.old_batch_size = self.data.batch_size
        self.automatic_optimization = False

    def val_dataloader(self):
        self.data.eval_batch_size = self.batch_size
        return self.data.val_dataloader()

    def validation_step(self, batch, batch_idx):
        return self.model.validation_step(batch, batch_idx)

    def train_dataloader(self):
        self.data.batch_size = self.batch_size
        return self.data.train_dataloader()

    def training_step(self, batch, batch_idx):
        return self.model.training_step(batch, batch_idx)

    def configure_optimizers(self):
        return self.model.configure_optimizers()


class Reducer(base.Reducer):
    @classmethod
    def reduce_model(cls, model: torch.nn.Module):
        """We do not want a new cache entry for every weight assignment Cache
        calculated result for each model dataset and task names.
        """
        return config.network, config.devices

    @classmethod
    def reduce_datamodule(cls, _: pl.LightningDataModule):
        # always using same data so ignore for cache path calculation for now
        return None


cache = decorator.cache(Reducer)


@cache
def get_max_batch_size(model: Model, data, method="validate"):
    tune_model = TuneModel(model, data)
    trainer = pl.Trainer(
        accelerator="auto",
        auto_scale_batch_size=True,
        devices=1,
        max_epochs=1,
        logger=False,
    )
    scale_batch_size_kwargs = {"init_val": config.batch_size}
    print(f"Calculating max {method} batch size")

    model.do_log = False
    old_batch_size = data.batch_size
    try:
        trainer.tune(
            tune_model,
            method=method,  # noqa
            scale_batch_size_kwargs=scale_batch_size_kwargs,
        )
    except ValueError:
        message = "Batch size of 2 does not fit in GPU, impossible to start training"
        raise Exception(message)

    model.do_log = True
    data.batch_size = old_batch_size

    safety_factor = (4 if config.devices > 1 else 2) if method == "validate" else 1
    max_batch_size = tune_model.batch_size // safety_factor
    max_batch_size |= 1  # max sure batch size at least one
    return max_batch_size
