from revnets import data

from revnets.networks import models
from revnets.networks.mediumnet_images import mediumnet


class Network(mediumnet.Network):
    @classmethod
    def get_model_module(cls):
        return models.mediumnet_images

    @classmethod
    def initialize_model(cls):
        return cls.get_model_module().Model(hidden_size1=100, hidden_size2=50)

    @classmethod
    def dataset(cls):
        return data.mnist.Dataset()
