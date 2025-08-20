from flask import Flask, render_template, request, jsonify, session
import numpy as np
import math
import time
import pickle

app = Flask(__name__)
app.secret_key = "paste_the_key_here"  # Change this to a random string!


class Connect4:
    def __init__(self):
        self.board = np.zeros((6, 7), dtype=int)
        self.current_player = 1  # 1 = human, 2 = AI
        self.move_count = 0
        self.game_start_time = time.time()
        self.game_ended = False

    def is_valid_move(self, col):
        return 0 <= col < 7 and self.board[0][col] == 0

    def make_move(self, col, player):
        for row in range(5, -1, -1):
            if self.board[row][col] == 0:
                self.board[row][col] = player
                self.move_count += 1
                return True
        return False

    def undo_move(self, col):
        for row in range(6):
            if self.board[row][col] != 0:
                self.board[row][col] = 0
                self.move_count -= 1
                return True
        return False

    def get_valid_moves(self):
        return [col for col in range(7) if self.is_valid_move(col)]

    def check_winner(self):
        # Horizontal
        for row in range(6):
            for col in range(4):
                if (
                    self.board[row][col] != 0
                    and self.board[row][col]
                    == self.board[row][col + 1]
                    == self.board[row][col + 2]
                    == self.board[row][col + 3]
                ):
                    return int(self.board[row][col])

        # Vertical
        for row in range(3):
            for col in range(7):
                if (
                    self.board[row][col] != 0
                    and self.board[row][col]
                    == self.board[row + 1][col]
                    == self.board[row + 2][col]
                    == self.board[row + 3][col]
                ):
                    return int(self.board[row][col])

        # Diagonal (/)
        for row in range(3, 6):
            for col in range(4):
                if (
                    self.board[row][col] != 0
                    and self.board[row][col]
                    == self.board[row - 1][col + 1]
                    == self.board[row - 2][col + 2]
                    == self.board[row - 3][col + 3]
                ):
                    return int(self.board[row][col])

        # Diagonal (\)
        for row in range(3):
            for col in range(4):
                if (
                    self.board[row][col] != 0
                    and self.board[row][col]
                    == self.board[row + 1][col + 1]
                    == self.board[row + 2][col + 2]
                    == self.board[row + 3][col + 3]
                ):
                    return int(self.board[row][col])

        return 0

    def is_board_full(self):
        return len(self.get_valid_moves()) == 0


class Connect4AI:
    def __init__(self, depth=5):
        self.depth = depth
        self.nodes_evaluated = 0

    def evaluate_position(self, game):
        winner = game.check_winner()
        if winner == 2:
            return 1000
        elif winner == 1:
            return -1000
        elif game.is_board_full():
            return 0

        score = 0
        center_count = sum(1 for row in range(6) if game.board[row][3] == 2)
        score += center_count * 3
        score += self.quick_threat_check(game)
        return score

    def quick_threat_check(self, game):
        score = 0
        for row in range(6):
            for col in range(4):
                window = [game.board[row][col + i] for i in range(4)]
                ai_count = window.count(2)
                human_count = window.count(1)
                empty_count = window.count(0)
                if ai_count == 3 and empty_count == 1:
                    score += 50
                elif human_count == 3 and empty_count == 1:
                    score -= 100
                elif ai_count == 2 and empty_count == 2:
                    score += 2
        return score

    def alpha_beta(self, game, depth, alpha, beta, is_maximizing):
        self.nodes_evaluated += 1
        winner = game.check_winner()
        if winner == 2:
            return 1000 + depth
        elif winner == 1:
            return -1000 - depth
        elif game.is_board_full() or depth == 0:
            return self.evaluate_position(game)
        valid_moves = game.get_valid_moves()
        valid_moves.sort(key=lambda x: abs(x - 3))
        if is_maximizing:
            max_eval = -math.inf
            for col in valid_moves:
                game.make_move(col, 2)
                eval_score = self.alpha_beta(game, depth - 1, alpha, beta, False)
                game.undo_move(col)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            for col in valid_moves:
                game.make_move(col, 1)
                eval_score = self.alpha_beta(game, depth - 1, alpha, beta, True)
                game.undo_move(col)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    def get_best_move(self, game):
        self.nodes_evaluated = 0
        start_time = time.time()
        best_move = 0
        best_value = -math.inf
        valid_moves = game.get_valid_moves()
        valid_moves.sort(key=lambda x: abs(x - 3))
        for col in valid_moves:
            game.make_move(col, 2)
            move_value = self.alpha_beta(
                game, self.depth - 1, -math.inf, math.inf, False
            )
            game.undo_move(col)
            if move_value > best_value:
                best_value = move_value
                best_move = col
        thinking_time = time.time() - start_time
        return best_move, thinking_time, self.nodes_evaluated


def get_game():
    if "game" in session:
        game = pickle.loads(session["game"])
    else:
        game = Connect4()
    return game


def save_game(game):
    session["game"] = pickle.dumps(game)


def get_ai():
    if "ai" in session:
        ai = pickle.loads(session["ai"])
    else:
        ai = Connect4AI(depth=5)
    return ai


def save_ai(ai):
    session["ai"] = pickle.dumps(ai)


def get_stats():
    if "game_stats" in session:
        return session["game_stats"]
    else:
        stats = {"human_wins": 0, "ai_wins": 0, "draws": 0}
        session["game_stats"] = stats
        return stats


def save_stats(stats):
    session["game_stats"] = stats


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_game_state", methods=["GET"])
def get_game_state():
    game = get_game()
    stats = get_stats()
    return jsonify(
        {
            "board": game.board.tolist(),
            "current_player": game.current_player,
            "message": "Ready to play!" if not game.game_ended else "Game ended!",
            "stats": stats,
            "game_active": not game.game_ended,
        }
    )


@app.route("/new_game", methods=["POST"])
def new_game():
    game = Connect4()
    ai = Connect4AI(depth=5)
    save_game(game)
    save_ai(ai)
    stats = get_stats()
    return jsonify(
        {
            "board": game.board.tolist(),
            "current_player": game.current_player,
            "message": "New game started! Your move!",
            "stats": stats,
        }
    )


@app.route("/reset_stats", methods=["POST"])
def reset_stats():
    stats = {"human_wins": 0, "ai_wins": 0, "draws": 0}
    save_stats(stats)
    return jsonify({"message": "Stats reset successfully! 🔄", "stats": stats})


@app.route("/make_move", methods=["POST"])
def make_move():
    game = get_game()
    ai = get_ai()
    stats = get_stats()
    if game.game_ended:
        return jsonify({"error": "Game has ended! Start a new game."})
    data = request.json
    col = data["column"]
    if not game.is_valid_move(col):
        return jsonify({"error": "Invalid move!"})
    game.make_move(col, 1)
    winner = game.check_winner()
    if winner == 1:
        stats["human_wins"] += 1
        game.game_ended = True
        save_game(game)
        save_stats(stats)
        return jsonify(
            {
                "board": game.board.tolist(),
                "winner": 1,
                "message": "🎉 Congratulations! You won! Ready for another round?",
                "stats": stats,
                "moves": game.move_count,
                "time": round(time.time() - game.game_start_time, 1),
            }
        )
    if game.is_board_full():
        stats["draws"] += 1
        game.game_ended = True
        save_game(game)
        save_stats(stats)
        return jsonify(
            {
                "board": game.board.tolist(),
                "winner": 0,
                "message": "It's a draw! Excellent game! 🤝",
                "stats": stats,
            }
        )
    ai_move, thinking_time, nodes = ai.get_best_move(game)
    game.make_move(ai_move, 2)
    winner = game.check_winner()
    if winner == 2:
        stats["ai_wins"] += 1
        game.game_ended = True
        save_game(game)
        save_ai(ai)
        save_stats(stats)
        return jsonify(
            {
                "board": game.board.tolist(),
                "winner": 2,
                "ai_move": ai_move,
                "message": "🤖 AI wins this round! Try again!",
                "stats": stats,
                "thinking_time": round(thinking_time, 2),
                "nodes_evaluated": nodes,
            }
        )
    if game.is_board_full() and not game.game_ended:
        stats["draws"] += 1
        game.game_ended = True
        save_game(game)
        save_ai(ai)
        save_stats(stats)
        return jsonify(
            {
                "board": game.board.tolist(),
                "winner": 0,
                "ai_move": ai_move,
                "message": "It's a draw! Great game! 🤝",
                "stats": stats,
            }
        )
    save_game(game)
    save_ai(ai)
    save_stats(stats)
    return jsonify(
        {
            "board": game.board.tolist(),
            "ai_move": ai_move,
            "current_player": 1,
            "message": f"AI played column {ai_move + 1}. Your turn!",
            "thinking_time": round(thinking_time, 2),
            "nodes_evaluated": nodes,
        }
    )


@app.route("/stats", methods=["GET"])
def stats():
    return jsonify(get_stats())


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8000)
