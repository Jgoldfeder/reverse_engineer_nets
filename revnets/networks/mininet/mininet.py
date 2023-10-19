from revnets.utils import config
from revnets.networks.mininet import mininet_untrained


class Network(mininet_untrained.Network):
    @classmethod
    def get_trained_network(cls):
        model = super().get_trained_network()
        cls.load_trained_weights(model, config.network_seed)
        return model
