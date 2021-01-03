import dictgeneratormodule as gen
import movemodule as mvm
import algebraicnotationmodule as alg
import random


class HashingAlgorithm:
    def gethashkey(self, listpiece, activecolor):
        pass

    def updatehashkey(self, key, listpiece, activecolor):
        pass


MIN64INT = -9223372036854775808
MAX64INT = 9223372036854775807


class Zobrist(HashingAlgorithm):
    def __init__(self):
        self.zarray = [[[self._getrandomnumber() for k in range(0, 64)] for j in range(0, 6)] for i in range(0, 2)]
        self.zenpassant = [self._getrandomnumber() for i in range(0, 8)]
        self.zcastle = [self._getrandomnumber() for i in range(0, 4)]
        self.zblackmove = self._getrandomnumber()

    @staticmethod
    def _getrandomnumber():
        return random.randint(MIN64INT, MAX64INT)

    @staticmethod
    def _getpiecetype(piece):
        if piece in ('wP', 'bP'):
            return 0
        elif piece in ('wR', 'bR'):
            return 1
        elif piece in ('wB', 'bB'):
            return 2
        elif piece in ('wN', 'bN'):
            return 3
        elif piece in ('wQ', 'bQ'):
            return 4
        elif piece in ('wK', 'bK'):
            return 5
        else:
            raise ValueError("Zobrist --> _getpiecetype : Not a valid piece!!!")

    @staticmethod
    def _getcellnumber(cell):
        return alg.celllist.index(cell)

    def gethashkey(self, listpiece, activecolor):
        zobristkey = 0
        if not activecolor:
            zobristkey ^= self.zblackmove
        for piece, cell in listpiece.get_white_pieces():
            piecetype = self._getpiecetype(piece)
            cellnumber = self._getcellnumber(cell)
            zobristkey ^= self.zarray[0][piecetype][cellnumber]
        for piece, cell in listpiece.get_black_pieces():
            piecetype = self._getpiecetype(piece)
            cellnumber = self._getcellnumber(cell)
            zobristkey ^= self.zarray[1][piecetype][cellnumber]
        for right in listpiece.get_white_castling_rights():
            index = 0
            if right is True:
                zobristkey ^= self.zcastle[index]
            index += 1
        for right in listpiece.get_black_castling_rights():
            index = 0
            if right is True:
                zobristkey ^= self.zcastle[index + 2]
            index += 1
        for cell in listpiece.get_enpassant_cells():
            zobristkey ^= self.zenpassant[cell.getfile() - 1]
        return zobristkey

    """
    def _getcastlingpiecestype(self):
        kingtype = self._getpiecetype(pcsm.King(alg.a1, mvm.CastlingRights()))
        rooktype = self._getpiecetype(pcsm.Rook(alg.a1, None, None))
        return kingtype, rooktype
    """

    @staticmethod
    def _getcastlingcells(move):
        if move.iskingcastling:
            if move.iswhiteturn:
                kingfrom = alg.celllist.index(alg.e1)
                kingto = alg.celllist.index(alg.g1)
                rookfrom = alg.celllist.index(alg.h1)
                rookto = alg.celllist.index(alg.f1)
            else:
                kingfrom = alg.celllist.index(alg.e8)
                kingto = alg.celllist.index(alg.g8)
                rookfrom = alg.celllist.index(alg.h8)
                rookto = alg.celllist.index(alg.f8)
        elif move.isqueencastling:
            if move.iswhiteturn:
                kingfrom = alg.celllist.index(alg.e1)
                kingto = alg.celllist.index(alg.c1)
                rookfrom = alg.celllist.index(alg.a1)
                rookto = alg.celllist.index(alg.d1)
            else:
                kingfrom = alg.celllist.index(alg.e8)
                kingto = alg.celllist.index(alg.c8)
                rookfrom = alg.celllist.index(alg.a8)
                rookto = alg.celllist.index(alg.d8)
        else:
            raise ValueError("Zobrist --> _getcastlingcells : Invalid castling move!!!")
        return kingfrom, kingto, rookfrom, rookto