from revnets.networks import models
from revnets.networks.mininet import mininet_untrained


class Network(mininet_untrained.Network):
    @classmethod
    def get_model_module(cls):
        return models.mediumnet
