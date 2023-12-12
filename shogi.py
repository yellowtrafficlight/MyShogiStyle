

class Piece:

    def __init__(self, type, is_sente, is_promoted = False):
        self.type = type
        self.sente = is_sente
        self.promoted = False

    def promote(self):
        self.promoted = True

    def __repr__(self):
        out = ""
        if self.promoted:
            out += "+"
        else:
            out += " "
        out += self.type
        if self.sente:
            out += "^"
        else:
            out += "v"
        return out

class Hand:

    def __init__(self):
        self.pieces = set()

    def add(self, piece):
        piece.promoted = False
        self.pieces.add(piece)

    def drop(self, piece_type):
        for p in self.pieces:
            if p.type == piece_type:
                self.pieces.remove(p)
                return p
        print("ERROR: No such piece on piece stand! " + piece_type)
        return None

    def __repr__(self):
        return str(self.pieces)

class ShogiBoard:

    def __init__(self):
        # using standard shogi coordinates
        board = [[None for i in range(9)] for i in range(9)]

        self.sente_hand = Hand()
        self.gote_hand = Hand()

        board[0][0] = Piece("L", False)
        board[0][1] = Piece("N", False)
        board[0][2] = Piece("S", False)
        board[0][3] = Piece("G", False)
        board[0][4] = Piece("K", False)
        board[0][5] = Piece("G", False)
        board[0][6] = Piece("S", False)
        board[0][7] = Piece("N", False)
        board[0][8] = Piece("L", False)

        board[1][1] = Piece("B", False)
        board[1][7] = Piece("R", False)
        for i in range(9):
            board[2][i] = Piece("P", False)

        board[8][0] = Piece("L", True)
        board[8][1] = Piece("N", True)
        board[8][2] = Piece("S", True)
        board[8][3] = Piece("G", True)
        board[8][4] = Piece("K", True)
        board[8][5] = Piece("G", True)
        board[8][6] = Piece("S", True)
        board[8][7] = Piece("N", True)
        board[8][8] = Piece("L", True)

        board[7][7] = Piece("B", True)
        board[7][1] = Piece("R", True)
        for i in range(9):
            board[6][i] = Piece("P", True)

        self.board = board     

    # origin and dest using standard shogi coordinates
    def move(self, sente, origin, dest, promote):

        o_row = origin[1] - 1
        o_col = origin[0] - 1 # order inverted because board is row then column
        d_row = dest[1] - 1
        d_col = dest[0] - 1
        if self.board[d_row][d_col] != None:
            self.board[d_row][d_col].sente = not self.board[d_row][d_col].sente
            if sente:
                self.sente_hand.add(self.board[d_row][d_col])
            else:
                self.gote_hand.add(self.board[d_row][d_col])
        
        self.board[d_row][d_col] = self.board[o_row][o_col]
        self.board[o_row][o_col] = None

        if promote:
            self.board[d_row][d_col].promote()


    def drop(self, sente, piece_type, dest):

        d_row = dest[1] - 1
        d_col = dest[0] - 1
        assert self.board[d_row][d_col] == None

        p = None
        if sente:
            p = self.sente_hand.drop(piece_type)
        else:
            p = self.gote_hand.drop(piece_type)
        self.board[d_row][d_col] = p

    def promote(self, square):
        self.board[square[1] - 1][square[0] - 1].promote()

    def __repr__(self):
        out = ""
        for r in self.board:
            rev = list(reversed(r))
            for i in range(8):
                out += str(rev[i]) + " "
            out += str(rev[8]) + "\n"

        out += "Sente hand: " + str(self.sente_hand) + "\n"
        out += "Gote hand: " + str(self.gote_hand) + "\n"
        return out



