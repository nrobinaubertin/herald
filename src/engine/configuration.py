from .transposition_table import TranspositionTable


class Config:

    def __init__(self, config_dict: dict = {}):
        self._config = config_dict
        self.name = "Herald"
        self.author = "nrobinaubertin"
        self.transposition_table = TranspositionTable({})
        self.qs_transposition_table = TranspositionTable({})
        self.opening_book: dict = {}

    def clear_transposition_tables(self):
        self.transposition_table = TranspositionTable({})
        self.qs_transposition_table = TranspositionTable({})

    @property
    def version(self):
        return self._config.get('version', True)

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
    def futility_pruning(self):
        return self._config.get('futility_pruning', False)

    @property
    def futility_depth(self):
        return self._config.get('futility_depth', 0)

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
