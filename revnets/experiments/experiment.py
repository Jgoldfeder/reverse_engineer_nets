from dataclasses import dataclass

import cli

from .. import evaluations, networks, reconstructions
from ..networks.base import Network
from ..utils import NamedClass, Path, Table, config


@dataclass
class Experiment(NamedClass):
    network: Network = None

    def run(self):
        config.show()
        for network_module in self.get_networks():
            self.network = network_module.Network()
            cli.console.rule(self.network.name)
            self.run_network()

    @classmethod
    def get_networks(cls):
        return (networks.mininet.mininet,)
        return (networks.mediumnet.mediumnet_40,)
        return networks.get_networks()

    def run_network(self):
        results = self.get_network_results()
        if results:
            table = self.make_table(results)
            table.show()
        self.save(results)

    def get_network_results(self):
        results = {}
        for technique in reconstructions.get_algorithms():
            reconstructor = technique.Reconstructor(self.network)
            reconstruction = reconstructor.reconstruct()
            evaluation = evaluations.evaluate(reconstruction, self.network)
            results[reconstructor.name] = evaluation
        return results

    @classmethod
    def make_table(cls, results):
        table = Table(show_lines=True)
        table.add_column("Technique", style="cyan", max_width=20, overflow="fold")

        metrics = next(iter(results.values())).metric_names()
        for name in metrics:
            table.add_column(name, style="magenta", max_width=13)
        for name, metrics in results.items():
            name = str(name)
            values = metrics.values()
            table.add_row(name, *values)

        return table

    @classmethod
    def get_base_name(cls):
        return Experiment.__module__

    def save(self, results):
        self.results_path.yaml = self.serialize_results(results)

    @property
    def results_path(self):  # noqa
        path = Path.results / self.name / self.network.name / "results.yaml"
        path = path.with_nonexistent_name()
        return path

    @classmethod
    def serialize_results(cls, results: dict[str, evaluations.Evaluation]):
        return {str(k): v.dict() for k, v in results.items()}