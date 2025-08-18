from flask import Flask, render_template, request, jsonify
import numpy as np
import math
import time

app = Flask(__name__)

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
                return True
        return False
    
    def get_valid_moves(self):
        return [col for col in range(7) if self.is_valid_move(col)]
    
    def check_winner(self):
        # Horizontal
        for row in range(6):
            for col in range(4):
                if (self.board[row][col] != 0 and
                    self.board[row][col] == self.board[row][col+1] == 
                    self.board[row][col+2] == self.board[row][col+3]):
                    return int(self.board[row][col])
        
        # Vertical
        for row in range(3):
            for col in range(7):
                if (self.board[row][col] != 0 and
                    self.board[row][col] == self.board[row+1][col] == 
                    self.board[row+2][col] == self.board[row+3][col]):
                    return int(self.board[row][col])
        
        # Diagonal (/)
        for row in range(3, 6):
            for col in range(4):
                if (self.board[row][col] != 0 and
                    self.board[row][col] == self.board[row-1][col+1] == 
                    self.board[row-2][col+2] == self.board[row-3][col+3]):
                    return int(self.board[row][col])
        
        # Diagonal (\)
        for row in range(3):
            for col in range(4):
                if (self.board[row][col] != 0 and
                    self.board[row][col] == self.board[row+1][col+1] == 
                    self.board[row+2][col+2] == self.board[row+3][col+3]):
                    return int(self.board[row][col])
        
        return 0
    
    def is_board_full(self):
        return len(self.get_valid_moves()) == 0

class Connect4AI:
    def __init__(self, depth=5):  # FIXED: Reduced from 7 to 5
        self.depth = depth
        self.nodes_evaluated = 0
    
    def evaluate_position(self, game):
        """Simpler and faster evaluation function"""
        winner = game.check_winner()
        if winner == 2:  # AI wins
            return 1000
        elif winner == 1:  # Human wins
            return -1000
        elif game.is_board_full():
            return 0
        
        score = 0
        
        # Simple center preference (much faster)
        center_count = sum(1 for row in range(6) if game.board[row][3] == 2)
        score += center_count * 3
        
        # Quick threat detection (only check immediate threats)
        score += self.quick_threat_check(game)
        
        return score
    
    def quick_threat_check(self, game):
        """Fast threat detection - only check obvious patterns"""
        score = 0
        
        # Check only a few key patterns instead of all windows
        for row in range(6):
            for col in range(4):  # Horizontal only
                window = [game.board[row][col+i] for i in range(4)]
                ai_count = window.count(2)
                human_count = window.count(1)
                empty_count = window.count(0)
                
                # Only score the most important patterns
                if ai_count == 3 and empty_count == 1:
                    score += 50
                elif human_count == 3 and empty_count == 1:
                    score -= 100  # Block human wins aggressively
                elif ai_count == 2 and empty_count == 2:
                    score += 2
        
        return score
    
    def alpha_beta(self, game, depth, alpha, beta, is_maximizing):
        self.nodes_evaluated += 1
        
        # Check for immediate wins/losses first
        winner = game.check_winner()
        if winner == 2:  # AI wins
            return 1000 + depth
        elif winner == 1:  # Human wins
            return -1000 - depth
        elif game.is_board_full() or depth == 0:
            return self.evaluate_position(game)
        
        valid_moves = game.get_valid_moves()
        
        # FIXED: Order moves for better pruning (center first)
        valid_moves.sort(key=lambda x: abs(x - 3))
        
        if is_maximizing:
            max_eval = -math.inf
            for col in valid_moves:
                game.make_move(col, 2)
                eval_score = self.alpha_beta(game, depth-1, alpha, beta, False)
                game.undo_move(col)
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break  # Prune more aggressively
            
            return max_eval
        
        else:
            min_eval = math.inf
            for col in valid_moves:
                game.make_move(col, 1)
                eval_score = self.alpha_beta(game, depth-1, alpha, beta, True)
                game.undo_move(col)
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break  # Prune more aggressively
            
            return min_eval
    
    def get_best_move(self, game):
        self.nodes_evaluated = 0
        start_time = time.time()
        
        best_move = 0
        best_value = -math.inf
        valid_moves = game.get_valid_moves()
        
        # FIXED: Try center columns first for better pruning
        valid_moves.sort(key=lambda x: abs(x - 3))
        
        for col in valid_moves:
            game.make_move(col, 2)
            move_value = self.alpha_beta(game, self.depth-1, -math.inf, math.inf, False)
            game.undo_move(col)
            
            if move_value > best_value:
                best_value = move_value
                best_move = col
        
        thinking_time = time.time() - start_time
        return best_move, thinking_time, self.nodes_evaluated

# Global instances
game = None
ai = None
game_stats = {"human_wins": 0, "ai_wins": 0, "draws": 0}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new_game', methods=['POST'])
def new_game():
    global game, ai
    game = Connect4()
    ai = Connect4AI(depth=5)  # FIXED: Faster depth
    return jsonify({
        'board': game.board.tolist(),
        'current_player': game.current_player,
        'message': 'New game started! Your move!',
        'stats': game_stats
    })

@app.route('/reset_stats', methods=['POST'])
def reset_stats():
    global game_stats, game
    game_stats = {"human_wins": 0, "ai_wins": 0, "draws": 0}
    game = None
    return jsonify({
        'message': 'Stats reset successfully! 🔄',
        'stats': game_stats
    })

@app.route('/make_move', methods=['POST'])
def make_move():
    global game, ai, game_stats
    
    if game is None or ai is None:
        return jsonify({'error': 'Please start a new game first!'})
    
    if game.game_ended:
        return jsonify({'error': 'Game has ended! Start a new game.'})
    
    data = request.json
    col = data['column']
    
    # Human move
    if not game.is_valid_move(col):
        return jsonify({'error': 'Invalid move!'})
    
    game.make_move(col, 1)
    
    # Check human win
    winner = game.check_winner()
    if winner == 1:
        game_stats["human_wins"] += 1
        game.game_ended = True
        return jsonify({
            'board': game.board.tolist(),
            'winner': 1,
            'message': '🎉 Congratulations! You won! Ready for another round? The AI learned from its mistakes... 🧠',
            'stats': game_stats,
            'moves': game.move_count,
            'time': round(time.time() - game.game_start_time, 1)
        })
    
    # Check draw after human move
    if game.is_board_full():
        game_stats["draws"] += 1
        game.game_ended = True
        return jsonify({
            'board': game.board.tolist(),
            'winner': 0,
            'message': "It's a draw! Excellent game! 🤝",
            'stats': game_stats
        })
    
    # AI move
    ai_move, thinking_time, nodes = ai.get_best_move(game)
    game.make_move(ai_move, 2)
    
    # Check AI win
    winner = game.check_winner()
    if winner == 2:
        game_stats["ai_wins"] += 1
        game.game_ended = True
        return jsonify({
            'board': game.board.tolist(),
            'winner': 2,
            'ai_move': ai_move,
            'message': '🤖 AI wins this round! Don\'t give up, try again!',
            'stats': game_stats,
            'thinking_time': round(thinking_time, 2),
            'nodes_evaluated': nodes
        })
    
    # Check draw after AI move
    if game.is_board_full() and not game.game_ended:
        game_stats["draws"] += 1
        game.game_ended = True
        return jsonify({
            'board': game.board.tolist(),
            'winner': 0,
            'ai_move': ai_move,
            'message': "It's a draw! Great game! 🤝",
            'stats': game_stats
        })
    
    # Game continues
    return jsonify({
        'board': game.board.tolist(),
        'ai_move': ai_move,
        'current_player': 1,
        'message': f'AI played column {ai_move + 1}. Your turn!',
        'thinking_time': round(thinking_time, 2),
        'nodes_evaluated': nodes
    })

@app.route('/stats', methods=['GET'])
def get_stats():
    return jsonify(game_stats)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8000)