# Connect 4 AI Game 🔴🟡

A modern, web-based Connect 4 game featuring an intelligent AI opponent powered by the Minimax algorithm with Alpha-Beta Pruning. Challenge yourself against a strategic AI that thinks 5 moves ahead!

## ✨ Features

- 🧠 **Intelligent AI Opponent** — Minimax with Alpha-Beta Pruning for strategic gameplay
- 👥 **Multi-User Support** — Each browser gets its own game session
- 📱 **Responsive Design** — Seamless experience on desktop, tablet, and mobile devices
- ⚡ **Fast Performance** — AI makes decisions in under 1 second
- 🎨 **Modern UI** — Clean interface with smooth animations and visual feedback
- 🎯 **Strategic Depth** — AI analyzes up to 5 moves ahead for challenging gameplay

## 🧠 AI Performance Metrics

| Metric                | Value                       |
|-----------------------|----------------------------|
| **Search Depth**      | 5 levels                   |
| **Average Response**  | < 1 second                 |
| **Nodes Evaluated**   | 10,000 - 50,000 per move   |
| **Algorithm**         | Minimax + Alpha-Beta Prune |
| **Difficulty Level**  | Challenging                |

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Git

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/viliusjan/connect4-ai.git
   cd connect4-ai
   ```

2. **Generate a Flask secret key**  
   Run this in Python:
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```
   Copy the generated string.

3. **Set your secret key in `connect4.py`**
   ```python
   app = Flask(__name__)
   app.secret_key = 'paste_your_generated_secret_key_here'
   ```

4. **Run the game locally**
   ```bash
   python3 connect4.py
   ```

5. **Open your browser**
   ```
   Navigate to: http://localhost:8000
   ```

## 📁 Project Structure

```
connect4-ai/
├── connect4.py          # Main Flask application (session-based, multi-user)
├── templates/           # HTML templates
└── README.md            # Project documentation
```

## 🎯 Game Rules

Connect 4 is a classic strategy game where players take turns dropping colored pieces into a grid:

- **Objective:** Be the first to get 4 pieces in a row
- **Winning Conditions:** Horizontal, vertical, or diagonal connections
- **Grid Size:** 7 columns × 6 rows
- **Turn-based:** Players alternate dropping pieces
- **Gravity Effect:** Pieces fall to the lowest available position

## 🧮 Algorithm Details

The AI uses a sophisticated decision-making process:

- **Minimax Algorithm:** Evaluates all possible future game states
- **Alpha-Beta Pruning:** Optimizes search by eliminating inferior branches
- **Evaluation Function:** Scores board positions based on strategic value
- **Depth Limitation:** Searches 5 moves ahead for optimal performance balance

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🐛 Issues & Support

Found a bug or have a suggestion? Please:

1. Check existing [issues](https://github.com/viliusjan/connect4-ai/issues)
2. Create a new issue with detailed description
3. Include steps to reproduce (if applicable)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Classic Connect 4 game concept by Milton Bradley
- Minimax algorithm implementation inspired by AI game theory
- Thanks to the Python and Flask communities

---

**Enjoy playing Connect 4 AI! 🎉**

*Challenge yourself against an intelligent opponent and improve your strategic skills.*
