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
algorithm = 'minmax'                    # default alphabeta
maxply = 4                 # default 5
transpositiontable = None
evalfunctype = 2
hashgenerator = None
rootposition = None
isrunning = True


def initnewgame():
    global nposition, totaltime, generationtime, evaluationtime, perfposition, nalphacut, nbetacut, nmatch
    global isrunning, transpositiontable, hashgenerator
    evm.functype = evalfunctype
    if isactivetraspositiontable:
        if hashingmethod == 'zobrist':
            hashgenerator = hsa.Zobrist()
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


class UciMoveSetter:
    def __init__(self, listpiece, strmoves, iswhiteturn):
        self.listpiece = listpiece
        self.strmoves = strmoves
        self.iswhiteturn = iswhiteturn

    def __call__(self):
        iswhiteturn = self.iswhiteturn
        for strmove in self.strmoves:
            fromcell = algn.str_to_algebraic(strmove[0:2])
            tocell = algn.str_to_algebraic(strmove[2:4])
            piece = self.listpiece.get_piece_by_cell(fromcell)
            capturedpiece = self.listpiece.get_piece_by_cell(tocell)
            promotionto = self.listpiece.get_promoted_piece(piece, tocell)
            if (fromcell, tocell) == (e1, h1) and piece == 'wK':
                move = mvm.Move(None, None, None, True, None, True, False, None, False, False)
            elif (fromcell, tocell) == (e1, a1) and piece == 'wK':
                move = mvm.Move(None, None, None, True, None, False, True, None, False, False)
            elif (fromcell, tocell) == (e8, h8) and piece == 'bK':
                move = mvm.Move(None, None, None, False, None, True, False, None, False, False)
            elif (fromcell, tocell) == (e8, a8) and piece == 'bK':
                move = mvm.Move(None, None, None, False, None, False, True, None, False, False)
            else:
                move = mvm.Move(piece, fromcell, tocell, iswhiteturn, capturedpiece, False, False, promotionto,
                                False, False)
            self.listpiece.applymove(move)
            iswhiteturn = not iswhiteturn


class FenStrParser:
    def __init__(self, algorithm, transpositiontable, hashgenerator):
        self.whiteletters = ('R', 'N', 'B', 'Q', 'K', 'P')
        self.blackletters = ('r', 'n', 'b', 'q', 'k', 'p')
        self.enginecolor = None
        self.startingcolor = None
        self.algorithm = algorithm
        self.transpositiontable = transpositiontable
        self.hashgenerator = hashgenerator
        self.listpiece = gen.list_piece_factory(self.hashgenerator)

    def _parse_castling_rights(self, castlingstring):
        whitekingside, whitequeenside, blackkingside, blackqueenside = False, False, False, False
        for right in castlingstring:
            if right is 'K':
                whitekingside = True
            elif right is 'Q':
                whitequeenside = True
            elif right is 'k':
                blackkingside = True
            elif right is 'q':
                blackqueenside = True
            elif right is '-':
                whitekingside, whitequeenside, blackkingside, blackqueenside = False, False, False, False
                break
            else:
                raise ValueError("gametreesearching.py : FenstrParser --> Invalid fen string!!!")
        self.listpiece.set_castlingrights(whitekingside, whitequeenside, blackkingside, blackqueenside)

    def _parse_pieces(self, boardstring):
        index = 0
        for char in boardstring:
            cell = algn.celllist[index]
            if char in ('1', '2', '3', '4', '5', '6', '7', '8'):
                index += int(char) - 1
            elif char == '/':
                continue
            elif char == 'R':
                self.listpiece.add_white_rook(cell)
            elif char == 'N':
                self.listpiece.add_white_knight(cell)
            elif char == 'B':
                self.listpiece.add_white_bishop(cell)
            elif char == 'Q':
                self.listpiece.add_white_queen(cell)
            elif char == 'K':
                self.listpiece.add_white_king(cell)
            elif char == 'P':
                self.listpiece.add_white_pawn(cell)
            elif char == 'r':
                self.listpiece.add_black_rook(cell)
            elif char == 'n':
                self.listpiece.add_black_knight(cell)
            elif char == 'b':
                self.listpiece.add_black_bishop(cell)
            elif char == 'q':
                self.listpiece.add_black_queen(cell)
            elif char == 'p':
                self.listpiece.add_black_pawn(cell)
            elif char == 'k':
                self.listpiece.add_black_king(cell)
            else:
                raise ValueError("gametreesearching.py : FenstrParser --> Invalid fen string!!!")
            index += 1

    def _parse_enpassant(self, enpassantstr):
        if enpassantstr == '-':
            return
        enpcoordinate = algn.str_to_algebraic(enpassantstr)
        self.listpiece.set_enpassant(enpcoordinate)

    @staticmethod
    def _get_start_color(startcolor):
        if startcolor == 'w':
            return True
        elif startcolor == 'b':
            return False
        else:
            raise ValueError("gametreesearching.py : FenstrParser --> Invalid fen string (not valid start color)!!!")

    @staticmethod
    def _get_active_color(startcolor, nummoves):
        if nummoves % 2 == 0:
            return startcolor
        else:
            return not startcolor

    def _parse_game_position(self):
        gameposition = None
        if self.algorithm == 'minmax':
            gameposition = MinimaxGamePosition(self.listpiece, self.enginecolor)
        elif self.algorithm == 'alphabeta' and self.transpositiontable:
            self.listpiece.set_origin_hash_value(self.enginecolor)
            gameposition = AlphabetaGamePositionTable(self.transpositiontable, self.listpiece, self.enginecolor)
            pass
        elif self.algorithm == 'alphabeta' and self.transpositiontable is None:
            gameposition = AlphabetaGamePosition(self.listpiece, self.enginecolor)
            pass
        elif self.algorithm == 'iterdeep' and self.transpositiontable is None:
            gameposition = IterativeDeepeningGamePosition(self.listpiece, self.enginecolor)
            pass
        elif self.algorithm == 'iterdeep' and self.transpositiontable is not None:
            # self.listpiece.set_origin_hash_value(self.enginecolor)
            # gameposition = IterativeDeepeningGamePositionTable(self.transpositiontable, self.listpiece, self.enginecolor)
            pass
        elif self.algorithm == 'perf':
            # gameposition = MinimaxPerfGamePosition(self.listpiece, self.enginecolor)
            pass
        else:
            raise ValueError("gametreesearching.py : FenstrParser --> not valid uci settings!!!")
        return gameposition

    def __call__(self, fenstr, movestr):
        tokens = fenstr
        if len(tokens) != 6:
            raise ValueError("Invalid FEN string!!!")
        self._parse_castling_rights(tokens[2])
        self._parse_pieces(tokens[0])
        self._parse_enpassant(tokens[3])
        if self.listpiece.isboardvalid() is False:
            raise ValueError("gametreesearching.py : FenstrParser --> Invalid fen string!!!")
        self.listpiece.update_castling_rights()
        iswhiteturnstart = self._get_start_color(tokens[1])
        movesetter = UciMoveSetter(self.listpiece, movestr, iswhiteturnstart)
        movesetter()
        self.enginecolor = self._get_active_color(iswhiteturnstart, len(movestr))
        gameposition = self._parse_game_position()
        return gameposition


# TODO Solo per debug
testfile = open("built_tree_test", "w")


class GamePosition:
    def __init__(self, listpiece, parent=None):
        self.iswhiteturn = None
        self.listpiece = listpiece
        self.parent = parent
        self.value = None
        self.moves = []
        self.children = []
        self.movegeneratorfunc = None
        self.enemy_game_position_func = None
        self.ischeckfunc = None
        self.imincheckmatevalue = None
        self.childrenevaluationfunc = None

    def applymove(self, move):
        self.listpiece.applymove(move)

    def undomove(self, move):
        self.listpiece.undomove(move)

    def removemove(self, move):
        self.moves.remove(move)

    def imincheckmate(self):
        if len(self.moves) < 1 and self.ischeckfunc():
            return True
        else:
            return False

    def isstalemate(self):
        if len(self.moves) < 1 and not self.ischeckfunc():
            return True
        if self.listpiece.is_stalemate():
            return True
        return False

    def calcbestmove(self, ply):
        raise Exception("GamePosition --> calcbestmove : not implemented!!!")

    def outputmoves(self):
        msg = ""
        for move in self.listpiece.moves:
            msg += move.short__str__() + " "
        msg += str(self.value)
        return msg

    def getrandomoutmove(self):
        index = random.randint(0, len(self.moves) - 1)
        strmove = self.moves[index].short__str__()
        return strmove

    @staticmethod
    def moveorderingkeybypriority(move):
        if move.ischeck:
            move.priority = 7
        elif move.capturedpiece:
            if move.capturedpiece in ('wQ', 'bQ', 'wR', 'bR', 'wB', 'bB', 'wN', 'bN'):
                move.priority = 6
            else:
                move.priority = 5
        elif move.iskingcastling:
            move.priority = 4
        elif move.isqueencastling:
            move.priority = 3
        elif move.promotionto:
            move.priority = 2
        else:
            move.priority = 1
        return move.priority


class WhiteGamePosition(GamePosition):
    def __init__(self, listpiece, parent=None):
        super().__init__(listpiece, parent)
        self.iswhiteturn = True
        self.movegeneratorfunc = gen.white_generator_moves
        self.enemy_game_position_func = BlackGamePosition
        self.ischeckfunc = self.listpiece.is_white_king_in_check
        self.imincheckmatevalue = -checkmatevalue
        self.childrenevaluationfunc = max
        self.generateallmoves()

    def generateallmoves(self):
        global generationtime
        starttime = time.perf_counter()
        for move in self.movegeneratorfunc():
            self.moves.append(move)
        generationtime += time.perf_counter() - starttime

    def __str__(self):
        msg = 'Active color: white\n'
        msg += str(self.listpiece)
        return msg


class WhiteGamePositionTable(WhiteGamePosition):
    def __init__(self, listpiece, transpositiontable, parent=None):
        super().__init__(listpiece, parent)
        self.enemy_game_position_func = BlackGamePositionTable
        self.transpositiontable = transpositiontable

    def gethashkey(self):
        return self.listpiece.gethashkey()

    def getrecord(self):
        key = self.listpiece.gethashkey()
        board = str(self.listpiece)
        record = self.transpositiontable.getrecord(key, board)
        return record

    def updatetranspositiontable(self, isalphacutoff, isbetacutoff, depthleft, bestmove, ishorizonleaf):
        self.transpositiontable.insertnewrecord(self.listpiece.gethashkey(), self.value, isalphacutoff, isbetacutoff,
                                                depthleft, bestmove, ishorizonleaf, str(self.listpiece))

    def refreshtranspositiontable(self):
        self.transpositiontable.updatetonewposition()


class BlackGamePosition(GamePosition):
    def __init__(self, listpiece, parent=None):
        super().__init__(listpiece, parent)
        self.iswhiteturn = False
        self.movegeneratorfunc = gen.black_generator_moves
        self.enemy_game_position_func = WhiteGamePosition
        self.ischeckfunc = self.listpiece.is_black_king_in_check
        self.imincheckmatevalue = checkmatevalue
        self.childrenevaluationfunc = min
        self.generateallmoves()

    def generateallmoves(self):
        global generationtime
        starttime = time.perf_counter()
        for move in self.movegeneratorfunc():
            self.moves.append(move)
        generationtime += time.perf_counter() - starttime

    def __str__(self):
        msg = 'Active color: black\n'
        msg += str(self.listpiece)
        return msg


class BlackGamePositionTable(BlackGamePosition):
    def __init__(self, listpiece, transpositiontable, parent=None):
        super().__init__(listpiece, parent)
        self.enemy_game_position_func = WhiteGamePositionTable
        self.transpositiontable = transpositiontable

    def gethashkey(self):
        return self.listpiece.gethashkey()

    def getrecord(self):
        key = self.listpiece.gethashkey()
        board = str(self.listpiece)
        record = self.transpositiontable.getrecord(key, board)
        return record

    def updatetranspositiontable(self, isalphacutoff, isbetacutoff, depthleft, bestmove, ishorizonleaf):
        self.transpositiontable.insertnewrecord(self.listpiece.gethashkey(), self.value, isalphacutoff, isbetacutoff,
                                                depthleft, bestmove, ishorizonleaf, str(self.listpiece))

    def refreshtranspositiontable(self):
        self.transpositiontable.updatetonewposition()


class MinimaxGamePosition:
    def __init__(self, listpiece, rootcolor):
        self.listpiece = listpiece
        self.rootcolor = rootcolor
        if rootcolor:
            self.position = WhiteGamePosition(listpiece)
        else:
            self.position = BlackGamePosition(listpiece)
        self.value = None

    @staticmethod
    def _childorderingkey(child):
        return child.value

    def minimaxformax(self, position, depthleft):
        global nposition
        nposition += 1
        if not isrunning:
            raise StopSearchSystemExit
        if depthleft == 0:
            evaluator = evm.Evaluator(position.listpiece)
            position.value = evaluator()
            msg = position.outputmoves()
            testfile.write(msg + "\n")
            return
        illegalmoves = []
        for move in position.moves:
            position.applymove(move)
            if self.listpiece.is_white_king_in_check():
                position.undomove(move)
                illegalmoves.append(move)
                continue
            child = position.enemy_game_position_func(position.listpiece, position)
            try:
                self.minimaxformin(child, depthleft - 1)
            except StopSearchSystemExit:
                position.undomove(move)
                raise StopSearchSystemExit
            position.children.append(child)
            position.undomove(move)
        for move in illegalmoves:
            position.removemove(move)
        if position.imincheckmate():
            position.value = position.imincheckmatevalue
            msg = position.outputmoves()
            testfile.write(msg + "****** CHECKMATE - GAME ENDED ******\n")
            return
        if position.isstalemate():
            position.value = 0
            msg = position.outputmoves()
            testfile.write(msg + "****** DRAW - GAME ENDED ******\n")
            return
        maxchild = None
        for child in position.children:
            if maxchild is None:
                maxchild = child
            else:
                if maxchild.value < child.value:
                    maxchild = child
        position.value = maxchild.value
        return

    def minimaxformin(self, position, depthleft):
        global nposition
        nposition += 1
        if not isrunning:
            raise StopSearchSystemExit
        if depthleft == 0:
            evaluator = evm.Evaluator(self.listpiece)
            position.value = evaluator()
            msg = position.outputmoves()
            testfile.write(msg + "\n")
            return
        illegalmoves = []
        for move in position.moves:
            position.applymove(move)
            if self.listpiece.is_black_king_in_check():
                position.undomove(move)
                illegalmoves.append(move)
                continue
            child = position.enemy_game_position_func(position.listpiece, position)
            try:
                self.minimaxformax(child, depthleft - 1)
            except StopSearchSystemExit:
                position.undomove(move)
                raise StopSearchSystemExit
            position.children.append(child)
            position.undomove(move)
        for move in illegalmoves:
            position.removemove(move)
        if position.imincheckmate():
            position.value = position.imincheckmatevalue
            msg = position.outputmoves()
            testfile.write(msg + "****** CHECKMATE - GAME ENDED ******\n")
            return
        if position.isstalemate():
            position.value = 0
            msg = position.outputmoves()
            testfile.write(msg + "****** DRAW - GAME ENDED ******\n")
            return
        minchild = None
        for child in position.children:
            if minchild is None:
                minchild = child
            else:
                if minchild.value > child.value:
                    minchild = child
        position.value = minchild.value
        return

    @staticmethod
    def _moveorderingkey(move):
        return move.value

    def calcbestmove(self, ply):
        global totaltime, evaluationtime
        starttime = time.perf_counter()
        if self.rootcolor:
            self.minimaxformax(self.position, ply)
        else:
            self.minimaxformin(self.position, ply)
        self.value = self.position.value
        for index in range(0, len(self.position.children)):
            if self.position.children[index].value == self.value:
                totaltime = time.perf_counter() - starttime
                evaluationtime = evm.evaluationtime
                return self.position.moves[index]

    def getrandomoutmove(self):
        index = random.randint(0, len(self.position.moves) - 1)
        strmove = self.position.moves[index].short__str__()
        return strmove

    def __str__(self):
        return self.position.__str__()


class AlphabetaGamePosition:
    def __init__(self, listpiece, rootcolor):
        self.listpiece = listpiece
        self.rootcolor = rootcolor
        if rootcolor:
            self.position = WhiteGamePosition(listpiece)
        else:
            self.position = BlackGamePosition(listpiece)
        self.value = None

    def alphabetamax(self, position, alpha, beta, depthleft):
        global nposition, isrunning, nalphacut, nbetacut
        nposition += 1
        if not isrunning:
            raise StopSearchSystemExit
        if depthleft == 0:
            evaluator = evm.Evaluator(position.listpiece)
            position.value = evaluator()
            msg = position.outputmoves()
            testfile.write(msg + "\n")
            return
        illegalmoves = []
        for move in position.moves:
            position.applymove(move)
            if self.listpiece.is_white_king_in_check():
                position.undomove(move)
                illegalmoves.append(move)
                continue
            child = position.enemy_game_position_func(position.listpiece, position)
            try:
                child.moves.sort(key=child.moveorderingkeybypriority, reverse=True)
                self.alphabetamin(child, alpha, beta, depthleft - 1)
            except StopSearchSystemExit:
                position.undomove(move)
                raise StopSearchSystemExit
            if child.value >= beta:
                position.value = beta
                msg = position.outputmoves()
                testfile.write(msg + "---------- beta cut-off -----------" + "\n")
                position.undomove(move)
                nbetacut += 1
                return
            if child.value > alpha:
                alpha = child.value
            position.children.append(child)
            position.undomove(move)
        for move in illegalmoves:
            position.removemove(move)
        if position.imincheckmate():
            position.value = position.imincheckmatevalue
            msg = position.outputmoves()
            testfile.write(msg + "********** CHECKMATE - GAME ENDED **********\n")
            return
        if position.isstalemate():
            position.value = 0
            msg = position.outputmoves()
            testfile.write(msg + "********** DRAW - GAME ENDED **********\n")
            return
        position.value = alpha
        return

    def alphabetamin(self, position, alpha, beta, depthleft):
        global nposition, isrunning, nalphacut, nbetacut
        nposition += 1
        if not isrunning:
            raise StopSearchSystemExit
        if depthleft == 0:
            evaluator = evm.Evaluator(position.listpiece)
            position.value = evaluator()
            msg = position.outputmoves()
            testfile.write(msg + "\n")
            return
        illegalmoves = []
        for move in position.moves:
            position.applymove(move)
            if self.listpiece.is_black_king_in_check():
                position.undomove(move)
                illegalmoves.append(move)
                continue
            child = position.enemy_game_position_func(position.listpiece, position)
            try:
                child.moves.sort(key=child.moveorderingkeybypriority, reverse=False)
                self.alphabetamax(child, alpha, beta, depthleft - 1)
            except StopSearchSystemExit:
                position.undomove(move)
                raise StopSearchSystemExit
            if child.value <= alpha:
                position.value = alpha
                msg = position.outputmoves()
                testfile.write(msg + "---------- alpha cut-off -----------" + "\n")
                position.undomove(move)
                nalphacut += 1
                return
            if child.value < beta:
                beta = child.value
            position.children.append(child)
            position.undomove(move)
        for move in illegalmoves:
            position.removemove(move)
        if position.imincheckmate():
            position.value = position.imincheckmatevalue
            msg = position.outputmoves()
            testfile.write(msg + "********** CHECKMATE - GAME ENDED **********\n")
            return
        if position.isstalemate():
            position.value = 0
            msg = position.outputmoves()
            testfile.write(msg + "********** DRAW - GAME ENDED **********\n")
            return
        position.value = beta
        return

    @staticmethod
    def _moveorderingkey(move):
        return move.value

    def calcbestmove(self, ply):
        global totaltime, evaluationtime
        starttime = time.perf_counter()
        if self.rootcolor:
            self.alphabetamax(self.position, -800, +800, ply)
        else:
            self.alphabetamin(self.position, -800, +800, ply)
        self.value = self.position.value
        for index in range(0, len(self.position.children)):
            if self.position.children[index].value == self.value:
                totaltime = time.perf_counter() - starttime
                evaluationtime = evm.evaluationtime
                return self.position.moves[index]

    def getrandomoutmove(self):
        index = random.randint(0, len(self.position.moves) - 1)
        strmove = self.position.moves[index].short__str__()
        return strmove

    def __str__(self):
        return self.position.__str__()


class AlphabetaGamePositionTable:
    def __init__(self, transpositiontable, listpiece, rootcolor):
        self.listpiece = listpiece
        self.rootcolor = rootcolor
        if rootcolor:
            self.position = WhiteGamePositionTable(listpiece, transpositiontable)
        else:
            self.position = BlackGamePositionTable(listpiece, transpositiontable)
        self.value = None

    def alphabetamax(self, position, alpha, beta, depthleft):
        global nposition, isrunning, nalphacut, nbetacut, nmatch
        nposition += 1
        if not isrunning:
            raise StopSearchSystemExit
        record = position.getrecord()
        if record is not None:
            position.value = record.score
            position.bestmove = record.bestmove
            msg = position.outputmoves()
            testfile.write(msg + "________ Transposition table match ______________" + "\n")
            nmatch += 1
            return
        if depthleft == 0:
            evaluator = evm.Evaluator(position.listpiece)
            position.value = evaluator()
            position.updatetranspositiontable(False, False, depthleft, None, True)
            msg = position.outputmoves()
            testfile.write(msg + "\n")
            return
        illegalmoves = []
        for move in position.moves:
            position.applymove(move)
            if self.listpiece.is_white_king_in_check():
                position.undomove(move)
                illegalmoves.append(move)
                continue
            child = position.enemy_game_position_func(position.listpiece, transpositiontable, position)
            try:
                child.moves.sort(key=child.moveorderingkeybypriority, reverse=True)
                self.alphabetamin(child, alpha, beta, depthleft - 1)
            except StopSearchSystemExit:
                position.listpiece.undomove(move)
                raise StopSearchSystemExit
            if child.value >= beta:
                position.value = beta
                position.updatetranspositiontable(False, True, depthleft, None, False)
                msg = position.outputmoves()
                testfile.write(msg + "---------- beta cut-off -----------" + "\n")
                position.undomove(move)
                nbetacut += 1
                return
            if child.value > alpha:
                alpha = child.value
            position.children.append(child)
            position.undomove(move)
        for move in illegalmoves:
            position.removemove(move)
        if position.imincheckmate():
            position.value = position.imincheckmatevalue
            position.updatetranspositiontable(False, False, depthleft, None, False)
            msg = position.outputmoves()
            testfile.write(msg + "********** CHECKMATE - GAME ENDED **********\n")
            return
        if position.isstalemate():
            position.value = 0
            position.updatetranspositiontable(False, False, depthleft, None, False)
            msg = position.outputmoves()
            testfile.write(msg + "********** DRAW - GAME ENDED **********\n")
            return
        position.value = alpha
        position.updatetranspositiontable(False, False, depthleft, None, False)
        return

    def alphabetamin(self, position, alpha, beta, depthleft):
        global nposition, isrunning, nalphacut, nbetacut, nmatch
        nposition += 1
        if not isrunning:
            raise StopSearchSystemExit
        record = position.getrecord()
        if record is not None:
            position.value = record.score
            position.bestmove = record.bestmove
            msg = position.outputmoves()
            testfile.write(msg + "________ Transposition table match ______________" + "\n")
            nmatch += 1
            return
        if depthleft == 0:
            evaluator = evm.Evaluator(position.listpiece)
            position.value = evaluator()
            position.updatetranspositiontable(False, False, depthleft, None, True)
            msg = position.outputmoves()
            testfile.write(msg + "\n")
            return
        illegalmoves = []
        for move in position.moves:
            position.applymove(move)
            if self.listpiece.is_white_king_in_check():
                position.undomove(move)
                illegalmoves.append(move)
                continue
            child = position.enemy_game_position_func(position.listpiece, transpositiontable, position)
            try:
                child.moves.sort(key=child.moveorderingkeybypriority, reverse=False)
                self.alphabetamax(child, alpha, beta, depthleft - 1)
            except StopSearchSystemExit:
                position.undomove(move)
                raise StopSearchSystemExit
            if child.value <= alpha:
                position.value = alpha
                position.updatetranspositiontable(True, False, depthleft, None, False)
                msg = position.outputmoves()
                testfile.write(msg + "---------- alpha cut-off -----------" + "\n")
                position.undomove(move)
                nalphacut += 1
                return
            if child.value < beta:
                beta = child.value
            position.children.append(child)
            position.undomove(move)
        for move in illegalmoves:
            position.removemove(move)
        if position.imincheckmate():
            position.value = position.imincheckmatevalue
            position.updatetranspositiontable(False, False, depthleft, None, False)
            msg = position.outputmoves()
            testfile.write(msg + "********** CHECKMATE - GAME ENDED **********\n")
            return
        if position.isstalemate():
            position.value = 0
            position.updatetranspositiontable(False, False, depthleft, None, False)
            msg = position.outputmoves()
            testfile.write(msg + "********** DRAW - GAME ENDED **********\n")
            return
        position.value = beta
        position.updatetranspositiontable(False, False, depthleft, None, False)
        return

    @staticmethod
    def _moveorderingkey(move):
        return move.value

    def calcbestmove(self, ply):
        global totaltime, evaluationtime
        starttime = time.clock()
        if self.rootcolor:
            self.alphabetamax(self.position, -800, +800, ply)
        else:
            self.alphabetamin(self.position, -800, +800, ply)
        self.value = self.position.value
        for index in range(0, len(self.position.children)):
            if self.position.children[index].value == self.value:
                totaltime = time.clock() - starttime
                evaluationtime = evm.evaluationtime
                return self.position.moves[index]

    def getrandomoutmove(self):
        index = random.randint(0, len(self.position.moves) - 1)
        strmove = self.position.moves[index].short__str__()
        return strmove

    def __str__(self):
        return self.position.__str__()


class IterativeDeepeningGamePosition:
    def __init__(self, listpiece, rootcolor):
        self.listpiece = listpiece
        self.rootcolor = rootcolor
        if rootcolor:
            self.position = WhiteGamePosition(listpiece)
        else:
            self.position = BlackGamePosition(listpiece)
        self.value = None

    def alphabetamax(self, position, alpha, beta, depthleft):
        global nposition, isrunning, nalphacut, nbetacut
        nposition += 1
        if not isrunning:
            raise StopSearchSystemExit
        if depthleft == 0:
            evaluator = evm.Evaluator(position.listpiece)
            position.value = evaluator()
            msg = position.outputmoves()
            testfile.write(msg + "\n")
            return
        illegalmoves = []
        for move in position.moves:
            position.applymove(move)
            if self.listpiece.is_white_king_in_check():
                position.undomove(move)
                illegalmoves.append(move)
                continue
            child = position.enemy_game_position_func(position.listpiece, position)
            try:
                child.moves.sort(key=child.moveorderingkeybypriority, reverse=True)
                self.alphabetamin(child, alpha, beta, depthleft - 1)
            except StopSearchSystemExit:
                position.undomove(move)
                raise StopSearchSystemExit
            if child.value >= beta:
                position.value = beta
                msg = position.outputmoves()
                testfile.write(msg + "---------- beta cut-off -----------" + "\n")
                position.undomove(move)
                nbetacut += 1
                return
            if child.value > alpha:
                alpha = child.value
            position.children.append(child)
            position.undomove(move)
        for move in illegalmoves:
            position.removemove(move)
        if position.imincheckmate():
            position.value = position.imincheckmatevalue
            msg = position.outputmoves()
            testfile.write(msg + "********** CHECKMATE - GAME ENDED **********\n")
            return
        if position.isstalemate():
            position.value = 0
            msg = position.outputmoves()
            testfile.write(msg + "********** DRAW - GAME ENDED **********\n")
            return
        position.value = alpha
        return

    def alphabetamin(self, position, alpha, beta, depthleft):
        global nposition, isrunning, nalphacut, nbetacut
        nposition += 1
        if not isrunning:
            raise StopSearchSystemExit
        if depthleft == 0:
            evaluator = evm.Evaluator(position.listpiece)
            position.value = evaluator()
            msg = position.outputmoves()
            testfile.write(msg + "\n")
            return
        illegalmoves = []
        for move in position.moves:
            position.applymove(move)
            if self.listpiece.is_black_king_in_check():
                position.undomove(move)
                illegalmoves.append(move)
                continue
            child = position.enemy_game_position_func(position.listpiece, position)
            try:
                child.moves.sort(key=child.moveorderingkeybypriority, reverse=False)
                self.alphabetamax(child, alpha, beta, depthleft - 1)
            except StopSearchSystemExit:
                position.undomove(move)
                raise StopSearchSystemExit
            if child.value <= alpha:
                position.value = alpha
                msg = position.outputmoves()
                testfile.write(msg + "---------- alpha cut-off -----------" + "\n")
                position.undomove(move)
                nalphacut += 1
                return
            if child.value < beta:
                beta = child.value
            position.children.append(child)
            position.undomove(move)
        for move in illegalmoves:
            position.removemove(move)
        if position.imincheckmate():
            position.value = position.imincheckmatevalue
            msg = position.outputmoves()
            testfile.write(msg + "********** CHECKMATE - GAME ENDED **********\n")
            return
        if position.isstalemate():
            position.value = 0
            msg = position.outputmoves()
            testfile.write(msg + "********** DRAW - GAME ENDED **********\n")
            return
        position.value = beta
        return

    @staticmethod
    def _moveorderingkey(move):
        return move.value

    def calcbestmove(self, maxply):
        global totaltime, evaluationtime
        starttime = time.perf_counter()
        for ply in range(1, maxply + 1):
            self.position.children = []
            if self.rootcolor:
                self.alphabetamax(self.position, -800, +800, ply)
            else:
                self.alphabetamin(self.position, -800, +800, ply)
            self.value = self.position.value
            for index in range(0, len(self.position.children)):
                self.position.moves[index].value = self.position.children[index].value
            self.position.moves.sort(key=self._moveorderingkey, reverse=True)
        totaltime = time.perf_counter() - starttime
        evaluationtime = evm.evaluationtime
        return self.position.moves[0]

    def getrandomoutmove(self):
        index = random.randint(0, len(self.position.moves) - 1)
        strmove = self.position.moves[index].short__str__()
        return strmove

    def __str__(self):
        return self.position.__str__()


if __name__ == '__main__':
    initnewgame()
    initgameposition("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0 moves".split())
    



    move1 = mvm.Move('wP', e2, e4, True, None, False, False, None, True, False)
    move2 = mvm.Move('bP', e7, e5, False, None, False, False, None, False, False)
    move3 = mvm.Move('wP', d2, d4, True, None, False, False, None, False, False)
    rootposition.listpiece.applymove(move1)
    rootposition.listpiece.applymove(move2)
    rootposition.listpiece.applymove(move3)
    newkey = rootposition.listpiece.gethashkey()
    print("Initial key: ", rootposition.listpiece.originhashvalue, "Final key: ", newkey)
    rootposition.listpiece.undomove(move3)
    rootposition.listpiece.undomove(move2)
    rootposition.listpiece.undomove(move1)

    rootposition.listpiece.applymove(move3)
    rootposition.listpiece.applymove(move2)
    rootposition.listpiece.applymove(move1)
    newkey = rootposition.listpiece.gethashkey()
    print("Transposition ", "Initial key: ", rootposition.listpiece.originhashvalue, "Final key: ", newkey)
