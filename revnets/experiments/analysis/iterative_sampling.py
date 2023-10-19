from dataclasses import dataclass

from revnets import networks, reconstructions
from revnets.experiments import experiment


@dataclass
class Experiment(experiment.Experiment):
    @classmethod
    def get_networks(cls):
        return (networks.mininet.mininet,)

    def run_network(self):
        technique = reconstructions.outputs_supervision.iterative_sampling.analysis
        reconstructor = technique.Reconstructor(self.network)
        reconstructor.reconstruct()
