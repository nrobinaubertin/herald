from typing import Optional

from .transposition_table import TranspositionTable


class Config:
    def __init__(self, config_dict: Optional[dict] = None):
        self._config = config_dict or {}
        self.name = "Herald"
        self.author = "nrobinaubertin"
        self.transposition_table = TranspositionTable({})
        self.opening_book: dict = {}

    def set_config(self, new_config: dict):
        self._config = new_config

    @property
    def version(self):
        return self._config.get("version")

    def set_depth(self, depth: int):
        self._config["depth"] = depth

    @property
    def depth(self):
        return self._config.get("depth", 0)

    @property
    def use_transposition_table(self):
        return self._config.get("use_transposition_table", False)

    @property
    def quiescence_search(self):
        return self._config.get("quiescence_search", False)

    @property
    def quiescence_depth(self):
        return self._config.get("quiescence_depth", 0)

    @property
    def eval_fn(self):
        return self._config["eval_fn"]

    @property
    def move_ordering_fn(self):
        return self._config["move_ordering_fn"]

    @property
    def qs_move_ordering_fn(self):
        return self._config["qs_move_ordering_fn"]

    @property
    def alg_fn(self):
        return self._config["alg_fn"]
