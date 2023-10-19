from revnets import data

from revnets.networks import models
from revnets.networks.mediumnet import mediumnet


class Network(mediumnet.Network):
    @classmethod
    def get_model_module(cls):
        return models.mediumnet_images

    @classmethod
    def initialize_model(cls):
        return cls.get_model_module().Model()

    @classmethod
    def dataset(cls):
        return data.mnist.Dataset()
