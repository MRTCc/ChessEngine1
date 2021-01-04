import dictgeneratormodule as gen
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

    def updatehashkey(self, key, listpiece, activecolor):
        newzobristkey = key
        if len(listpiece.moves) < 1:
            raise ValueError("Zobrist --> updatezobristkey : no update needed, because there are no moves applied!!!")
        move = listpiece.moves[-1]
        if move.iswhiteturn != activecolor:
            newzobristkey ^= self.zblackmove
        for index in range(0, len(listpiece.changedenpassant)):
            if listpiece.changedenpassant[index]:
                newzobristkey ^= self.zenpassant[index]
        for index in range(0, len(listpiece.changedcastling)):
            if listpiece.changedcastling[index]:
                newzobristkey ^= self.zcastle[index]
        if move.iswhiteturn:
            color = 0
            capturepiececolor = 1
        else:
            color = 1
            capturepiececolor = 0
        if move.piece is not None:
            piecetype = self._getpiecetype(move.piece)
            cellnumber = self._getcellnumber(move.fromcell)
            newzobristkey ^= self.zarray[color][piecetype][cellnumber]
            if move.capturedpiece is not None:
                if move.tocell in gen.enpassantcells:
                    if move.iswhiteturn:
                        hitcell = move.tocell.sumcoordinate(0, -1)
                    else:
                        hitcell = move.tocell.sumcoordinate(0, +1)
                else:
                    hitcell = move.tocell
                piecetype = self._getpiecetype(move.capturedpiece)
                cellnumber = self._getcellnumber(hitcell)
                newzobristkey ^= self.zarray[capturepiececolor][piecetype][cellnumber]
            if move.promotionto is not None:
                piecetype = self._getpiecetype(move.promotionto)
            else:
                piecetype = self._getpiecetype(move.piece)
            cellnumber = self._getcellnumber(move.fromcell)
            newzobristkey ^= self.zarray[color][piecetype][cellnumber]
        else:

            if move.iswhiteturn:
                if move.iskingcastling:
                    kingtype = self._getpiecetype('wK')
                    rooktype = self._getpiecetype('wR')
                    kingfromnumber = self._getcellnumber(alg.e1)
                    kingtonumber = self._getcellnumber(alg.g1)
                    rookfromnumber = self._getcellnumber(alg.h1)
                    rooktonumber = self._getcellnumber(alg.f1)
                    newzobristkey ^= self.zarray[0][kingtype][kingfromnumber]
                    newzobristkey ^= self.zarray[0][kingtype][kingtonumber]
                    newzobristkey ^= self.zarray[0][rooktype][rookfromnumber]
                    newzobristkey ^= self.zarray[0][rooktype][rooktonumber]
                if move.isqueencastling:
                    kingtype = self._getpiecetype('wK')
                    rooktype = self._getpiecetype('wR')
                    kingfromnumber = self._getcellnumber(alg.e1)
                    kingtonumber = self._getcellnumber(alg.c1)
                    rookfromnumber = self._getcellnumber(alg.a1)
                    rooktonumber = self._getcellnumber(alg.d1)
                    newzobristkey ^= self.zarray[0][kingtype][kingfromnumber]
                    newzobristkey ^= self.zarray[0][kingtype][kingtonumber]
                    newzobristkey ^= self.zarray[0][rooktype][rookfromnumber]
                    newzobristkey ^= self.zarray[0][rooktype][rooktonumber]
            else:
                if move.iskingcastling:
                    kingtype = self._getpiecetype('bK')
                    rooktype = self._getpiecetype('bR')
                    kingfromnumber = self._getcellnumber(alg.e8)
                    kingtonumber = self._getcellnumber(alg.g8)
                    rookfromnumber = self._getcellnumber(alg.h8)
                    rooktonumber = self._getcellnumber(alg.f8)
                    newzobristkey ^= self.zarray[1][kingtype][kingfromnumber]
                    newzobristkey ^= self.zarray[1][kingtype][kingtonumber]
                    newzobristkey ^= self.zarray[1][rooktype][rookfromnumber]
                    newzobristkey ^= self.zarray[1][rooktype][rooktonumber]
                if move.isqueencastling:
                    kingtype = self._getpiecetype('bK')
                    rooktype = self._getpiecetype('bR')
                    kingfromnumber = self._getcellnumber(alg.e8)
                    kingtonumber = self._getcellnumber(alg.c8)
                    rookfromnumber = self._getcellnumber(alg.a8)
                    rooktonumber = self._getcellnumber(alg.d8)
                    newzobristkey ^= self.zarray[1][kingtype][kingfromnumber]
                    newzobristkey ^= self.zarray[1][kingtype][kingtonumber]
                    newzobristkey ^= self.zarray[1][rooktype][rookfromnumber]
                    newzobristkey ^= self.zarray[1][rooktype][rooktonumber]
        return newzobristkey
