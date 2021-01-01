import time
import algebraicnotationmodule as algn
from algebraicnotationmodule import (a8, b8, c8, d8, e8, f8, g8, h8,
                                     a7, b7, c7, d7, e7, f7, g7, h7,
                                     a6, b6, c6, d6, e6, f6, g6, h6,
                                     a5, b5, c5, d5, e5, f5, g5, h5,
                                     a4, b4, c4, d4, e4, f4, g4, h4,
                                     a3, b3, c3, d3, e3, f3, g3, h3,
                                     a2, b2, c2, d2, e2, f2, g2, h2,
                                     a1, b1, c1, d1, e1, f1, g1, h1)

evaluationtime = 0

pawnvalue = 1
rookvalue = 5
knightvalue = 3
bishopvalue = 3
queenvalue = 9
doublepawnvalue = 0.5
isolatedpawnvalue = 0.5
blockedpawnvalue = 0.75
kingvalue = 1000

functype = 0


def Evaluator(listpiece):
    if functype == 0:
        # per ora disattivo queta parte
        # return EvaluationFuncTable(listpiece)
        pass
    elif functype == 1:
        return EvaluationFuncLazy(listpiece)
    else:
        raise Exception("evaluationmodule.py : Evaluator --> invalid functype!!!")


class EvaluationFunc:
    def __init__(self, listpiece):
        self.listpiece = listpiece
        self.wdoubledpawns, self.bdoubledpawns = self.listpiece.count_doubled_pawns()
        self.wblockedpawns, self.bblockedpawns = self.listpiece.count_blocked_pawns()
        self.wisolatedpawns, self.bisolatedpawns = self.listpiece.count_isolated_pawns()
        self.mobility = 0
        self.evaluation = None

    def __call__(self):
        raise Exception("evaluationmodule.py : EvaluationFunc --> __call__ --> not implemented!!!")


class EvaluationFuncLazy(EvaluationFunc):
    def __init__(self, listpiece):
        super().__init__(listpiece)

    @staticmethod
    def _set_white_evaluation_parameters(piece):
        if piece == 'wP':
            piecevalue = pawnvalue
        elif piece == 'wR':
            piecevalue = rookvalue
        elif piece == 'wN':
            piecevalue = knightvalue
        elif piece == 'wB':
            piecevalue = bishopvalue
        elif piece == 'wQ':
            piecevalue = queenvalue
        elif piece == 'wK':
            piecevalue = kingvalue
        else:
            raise ValueError("Not a valid piece!!!")
        return piecevalue

    @staticmethod
    def _set_black_evaluation_parameters(piece):
        if piece == 'bP':
            piecevalue = pawnvalue
        elif piece == 'bR':
            piecevalue = rookvalue
        elif piece == 'bN':
            piecevalue = knightvalue
        elif piece == 'bB':
            piecevalue = bishopvalue
        elif piece == 'bQ':
            piecevalue = queenvalue
        elif piece == 'bK':
            piecevalue = kingvalue
        else:
            raise ValueError("Not a valid piece!!!")
        return piecevalue

    def __call__(self):
        global evaluationtime
        starttime = time.clock()
        self.evaluation = 0
        whitevalue = 0
        blackvalue = 0
        for piece in self.listpiece.whitepieces():
            value = self._set_white_evaluation_parameters(piece)
            whitevalue += value
        for piece in self.listpiece.blackpieces():
            value = self._set_black_evaluation_parameters(piece)
            blackvalue += value
        self.evaluation = whitevalue - blackvalue
        doubledpawns = (self.wdoubledpawns - self.bdoubledpawns) * doublepawnvalue
        isolatedpawns = (self.wisolatedpawns - self.bisolatedpawns) * isolatedpawnvalue
        blockedpawns = (self.wblockedpawns - self.bblockedpawns) * blockedpawnvalue
        self.evaluation += doubledpawns + isolatedpawns + blockedpawns
        evaluationtime += time.clock() - starttime
        return self.evaluation
