import constants

class Move():
    def __init__(self, uci):
        self.uci = uci

    @property
    def from_square(self):
        return self.uci[:2]

    @property
    def to_square(self):
        return self.uci[2:4]

    @property
    def promotion(self):
        if len(uci) == 5:
            return self.uci[4]
        else:
            None
