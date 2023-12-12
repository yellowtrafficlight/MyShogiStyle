import os
import pandas as pd

import pykakasi

from shogi import *

class PlayerFeatures:

    def __init__(self):
        self.move_count = {}
        self.move_count["P"] = 0
        self.move_count["L"] = 0
        self.move_count["N"] = 0
        self.move_count["S"] = 0
        self.move_count["G"] = 0
        self.move_count["B"] = 0
        self.move_count["R"] = 0
        self.move_count["K"] = 0

        self.hand_avg = 0
        self.promote = 0
        self.sacrifice = 0
        self.castling = 0

        self.king_col = 4

    def update(self, move, board, hand, is_sacrifice):
        dest = move["Dest"]
        piece = board.board[dest[1] - 1][dest[0] - 1] # order inverted because board is row then column
        self.move_count[piece.type] += 1

        if piece.type == "K":
            self.king_col = dest[0] - 1

        if move["Promote"]:
            self.promote += 1

        if is_sacrifice:
            self.sacrifice += 1

        self.hand_avg += len(hand.pieces)

    # performs a single update, only called before the first sacrifice
    def update_castling(self):
        self.castling += abs(self.king_col - 4)

    def average(self, move_count):

        self.move_count["P"] /= move_count
        self.move_count["L"] /= move_count
        self.move_count["N"] /= move_count
        self.move_count["S"] /= move_count
        self.move_count["G"] /= move_count
        self.move_count["B"] /= move_count
        self.move_count["R"] /= move_count
        self.move_count["K"] /= move_count

        self.promote /= move_count
        self.hand_avg /= move_count
        self.sacrifice /= move_count


def parse_move(move, prev_dest):

    kks = pykakasi.kakasi()
    out = {}

    # print(move)

    first = kks.convert(move[0])[0]['hepburn']
    if first == "dou":
        out["Recapture"] = True
        out["Dest"] = prev_dest
        out["Drop"] = False
    else:
        out["Recapture"] = False
        col = int(first)
        second = kks.convert(move[1])[0]['hepburn']
        if second == "ichi":
            row = 1
        elif second == "ni":
            row = 2
        elif second == "san":
            row = 3
        elif second == "shi":
            row = 4
        elif second == "go":
            row = 5
        elif second == "roku":
            row = 6
        elif second == "shichi":
            row = 7
        elif second == "hachi":
            row = 8
        elif second == "kyuu":
            row = 9
        out["Dest"] = (col, row)
    
    out["Drop"] = kks.convert(move[3])[0]['hepburn'] == "da"
    out["Promote"] = kks.convert(move[3])[0]['hepburn'] == "sei"

    if out["Drop"]:
        piece_type = kks.convert(move[2])[0]['hepburn']
        if piece_type == "ho":
            out["Piece"] = "P"
        elif piece_type == "kaori":
            out["Piece"] = "L"
        elif piece_type == "katsura":
            out["Piece"] = "N"
        elif piece_type == "gin":
            out["Piece"] = "S"
        elif piece_type == "kin":
            out["Piece"] = "G"
        elif piece_type == "kaku":
            out["Piece"] = "B"
        elif piece_type == "hi":
            out["Piece"] = "R"
        out["Origin"] = "Piece stand / hand"
    else:
        col = int(move[-3])
        row = int(move[-2])
        out["Origin"] = (col, row)

    return out
    
def execute_move(board, move, sente, prev_dest):
    if move["Drop"]:
        board.drop(sente, move["Piece"], move["Dest"])
        dest = move["Dest"]
    else:
        if move["Recapture"]:
            dest = prev_dest
        else:
            dest = move["Dest"]
        board.move(sente, move["Origin"], dest, move["Promote"])
    return dest

def center_diff(board):
    center_diff_now = 0
    for i in range(3, 6):
        for j in range(3, 6):
            p = board.board[i][j]
            if p is not None:
                if p.type == "S" or p.type == "G":
                    center_diff_now = -2 + 4 * p.sente
                else:
                    center_diff_now = -1 + 2 * p.sente
    return center_diff_now

# returns true only for classical edge attacks beginning with a pawn
def is_edge_atk(board, move, sente):
    dest = move["Dest"]
    if dest[0] != 1 and dest[0] != 9:
        return False
    if board.board[dest[1] - 1][dest[0] - 1].type != "P":
        return False
    if (sente and dest[1] == 1) or (not sente and dest[1] == 9):
        return False
    front = board.board[dest[1] - 2 * sente][dest[0] - 1]
    return front is not None and front.type == "P"

if __name__ == "__main__":

    games = pd.DataFrame(columns = ["P", "L", "N", "S", "G", "B", "R", "K",
                                    "promote_avg", "hand_avg", "major_diff_avg", "center_diff_avg",
                                    "edge_atk_diff", "castling_diff", "sacrifice_diff",
                                    "first_sacrifice", "am_i_sente"])

    for filename in os.listdir("./data/"):
        with open("./data/" + filename, 'r') as f:

            content = f.readlines()
            if "81Dojo" in filename:
                content = content[:-1]

            # find sente and gote
            if "iongrey" in content[4]:
                i_am_sente = 1
            else:
                i_am_sente = 0

            while content[0].strip()[0] != "1":
                content.pop(0)

            # replaying the game

            b = ShogiBoard()
            prev_dest = None
            sente = True
            move_count = 0
            major_diff_cum = 0
            major_diff_now = 0
            first_sacrifice = 0
            losing_capture = False
            is_sacrifice = False
            center_diff_cum = 0
            edge_atk_diff = 0

            sente_features = PlayerFeatures()
            gote_features = PlayerFeatures()

            for l in content:
                if len(l) == 1:
                    # print("End of game")
                    break
                if l[0] != " " and not l[0].isdigit():
                    continue
                if "81Dojo" in filename:
                    raw_move = l.split(" ")[-4].rstrip()
                else:
                    raw_move = l.split(" ")[-1].rstrip()
                move = parse_move(raw_move, prev_dest)
                dest = move["Dest"]
                target = b.board[dest[1] - 1][dest[0] - 1] # order inverted because board is row then column
                if target is not None and (target.type == "B" or target.type == "R"):
                    major_diff_now += 2 * sente - 1
                major_diff_cum += major_diff_now
                if losing_capture:
                    if not move["Recapture"]:
                        if first_sacrifice == 0:
                            first_sacrifice = 2 * sente - 1
                            sente_features.castling /= move_count
                            gote_features.castling /= move_count
                        is_sacrifice = True
                    losing_capture = False
                else:
                    if move["Recapture"]:
                        losing_capture = True

                prev_dest = execute_move(b, move, sente, prev_dest)

                center_diff_cum += center_diff(b)
                if is_edge_atk(b, move, sente):
                    edge_atk_diff += 2 * sente - 1
                if sente:
                    sente_features.update(move, b, b.sente_hand, is_sacrifice)
                else:
                    gote_features.update(move, b, b.gote_hand, is_sacrifice)
                if first_sacrifice == 0:
                    sente_features.update_castling()
                    gote_features.update_castling()
                sente = not sente
                is_sacrifice = False
                move_count += 1

            sente_features.average(move_count)
            gote_features.average(move_count)
            major_diff_cum /= move_count
            center_diff_cum /= move_count
            edge_atk_diff /= move_count

            games.loc[len(games.index)] = [sente_features.move_count["P"] - gote_features.move_count["P"], sente_features.move_count["L"] - gote_features.move_count["L"],
                                           sente_features.move_count["N"] - gote_features.move_count["N"], sente_features.move_count["S"] - gote_features.move_count["S"],
                                           sente_features.move_count["G"] - gote_features.move_count["G"], sente_features.move_count["B"] - gote_features.move_count["B"],
                                           sente_features.move_count["R"] - gote_features.move_count["R"], sente_features.move_count["K"] - gote_features.move_count["K"],
                                           sente_features.promote - gote_features.promote, sente_features.hand_avg - gote_features.hand_avg, 
                                           major_diff_cum, center_diff_cum, edge_atk_diff,
                                           sente_features.castling - gote_features.castling, sente_features.sacrifice - gote_features.sacrifice,
                                           first_sacrifice, i_am_sente]

    games.to_csv("feature_table.csv", index=False)



