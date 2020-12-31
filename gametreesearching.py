import movemodule as mvm
import dictgeneratormodule as gen
import random
import time
import evaluationmodule as evm
import transpositionmodule as trsp
import algebraicnotationmodule as algn
import hashingalgorithms as hsa
from algebraicnotationmodule import (a8, b8, c8, d8, e8, f8, g8, h8,
                                     a7, b7, c7, d7, e7, f7, g7, h7,
                                     a6, b6, c6, d6, e6, f6, g6, h6,
                                     a5, b5, c5, d5, e5, f5, g5, h5,
                                     a4, b4, c4, d4, e4, f4, g4, h4,
                                     a3, b3, c3, d3, e3, f3, g3, h3,
                                     a2, b2, c2, d2, e2, f2, g2, h2,
                                     a1, b1, c1, d1, e1, f1, g1, h1)


class StopSearchSystemExit(SystemExit):
    pass


# statistic data
nposition = 0
perfposition = 0
nalphacut = 0
nbetacut = 0
nmatch = 0
totaltime = 0
generationtime = 0
evaluationtime = 0


# engine settings
checkmatevalue = 10000
hashingmethod = 'zobrist'
isactivetraspositiontable = False     # default True
algorithm = 'iterdeep'                    # default alphabeta
maxply = 3                    # default 5
transpositiontable = None
evalfunctype = 1
hashgenerator = None
rootposition = None
isrunning = True


def initnewgame():
    global nposition, totaltime, generationtime, evaluationtime, perfposition, nalphacut, nbetacut, nmatch
    global isrunning, transpositiontable, hashgenerator
    evm.functype = evalfunctype
    if isactivetraspositiontable:
        if hashingmethod == 'zobrist':
            # TODO mettere a posto HASHINGALGORITHMS
            # hashgenerator = hsa.Zobrist()
            pass
        transpositiontable = trsp.transpositiontablefactory(algorithm)
    nposition = 0
    perfposition = 0
    nalphacut = 0
    nbetacut = 0
    nmatch = 0
    totaltime = 0
    generationtime = 0
    evaluationtime = 0


def initgameposition(tokens):
    global nposition, totaltime, generationtime, evaluationtime, perfposition, nalphacut, nbetacut, nmatch
    global isrunning, transpositiontable, hashgenerator
    if transpositiontable:
        transpositiontable.updatetonewposition()
    global isrunning
    isrunning = True
    global rootposition
    movestr = []
    fenstr = []
    if tokens[0] == 'startpos':
        fenstr.append('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR')
        fenstr.append('w')
        fenstr.append('-')
        fenstr.append('-')
        fenstr.append('0')
        fenstr.append('0')
        isamove = False
        for token in tokens:
            if token == 'moves':
                isamove = True
                continue
            if isamove:
                movestr.append(token)
    else:
        isfenstr = True
        for token in tokens:
            if token == 'moves':
                isfenstr = False
                continue
            if isfenstr:
                fenstr.append(token)
            else:
                movestr.append(token)
    fenparser = FenStrParser(algorithm, transpositiontable, hashgenerator)
    rootposition = fenparser(fenstr, movestr)
    nposition = 0
    perfposition = 0
    nalphacut = 0
    nbetacut = 0
    nmatch = 0
    totaltime = 0
    generationtime = 0
    evaluationtime = 0


class FenStrParser:
    def __init__(self, algorithm, transpositiontable, hashgenerator):
        self.whiteletters = ('R', 'N', 'B', 'Q', 'K', 'P')
        self.blackletters = ('r', 'n', 'b', 'q', 'k', 'p')
        self.enginecolor = None
        self.startingcolor = None
        self.algorithm = algorithm
        self.transpositiontable = transpositiontable
        self.hashgenerator = hashgenerator

    def _isboardvalid(self, token):
        pass

    def __call__(self, fenstr, movestr):
        tokens = fenstr
        if len(tokens) != 6:
            raise ValueError("Invalid FEN string!!!")
        self._isboardvalid(tokens[0])
        pass