from .transposition_table import TranspositionTable


class Config:

    def __init__(self, config_dict: dict = {}):
        self._config = config_dict
        self.name = "Herald"
        self.version = "0.19.0"
        self.author = "nrobinaubertin"
        self.transposition_table = TranspositionTable({})
        self.qs_transposition_table = TranspositionTable({})
        self.opening_book: dict = {}

    def clear_transposition_tables(self):
        self.transposition_table = TranspositionTable({})
        self.qs_transposition_table = TranspositionTable({})

    @property
    def use_transposition_table(self):
        return self._config.get('use_transposition_table', True)

    @property
    def use_qs_transposition_table(self):
        return self._config.get('use_qs_transposition_table', True)

    @property
    def quiescence_search(self):
        return self._config.get('quiescence_search', False)

    @property
    def quiescence_depth(self):
        return self._config.get('quiescence_depth', 0)

    @property
    def eval_fn(self):
        return self._config['eval_fn']

    @property
    def move_ordering_fn(self):
        return self._config['move_ordering_fn']

    @property
    def alg_fn(self):
        return self._config['alg_fn']
