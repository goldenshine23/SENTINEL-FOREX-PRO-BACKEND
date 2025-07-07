import json
import os
from datetime import datetime

MEMORY_FILE = "ai_memory.json"

class AIMemory:
    def __init__(self):
        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True) if os.path.dirname(MEMORY_FILE) else None
        if not os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "w") as f:
                json.dump({}, f)
        self.load_memory()

    def load_memory(self):
        try:
            with open(MEMORY_FILE, "r") as f:
                self.memory = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            self.memory = {}

    def save_memory(self):
        with open(MEMORY_FILE, "w") as f:
            json.dump(self.memory, f, indent=2)

    def record_trade(self, symbol, entry_price, exit_price, profit, sentiment=None, bias=None, timestamp=None):
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat()

        if symbol not in self.memory:
            self.memory[symbol] = []

        self.memory[symbol].append({
            "entry_price": entry_price,
            "exit_price": exit_price,
            "profit": profit,
            "sentiment": sentiment,
            "bias": bias,
            "timestamp": timestamp,
        })
        self.save_memory()

    def get_recent_trades(self, symbol, limit=10):
        trades = self.memory.get(symbol, [])
        return trades[-limit:] if trades else []

    def analyze_pattern(self, symbol):
        recent_trades = self.get_recent_trades(symbol)
        losses = [t for t in recent_trades if t.get('profit') is not None and t['profit'] < 0]
        wins = [t for t in recent_trades if t.get('profit') is not None and t['profit'] > 0]

        analysis = {
            "adjust_risk": False,
            "streak_loss": len(losses) >= 3,
            "streak_win": len(wins) >= 3,
            "last_sentiment": recent_trades[-1].get('sentiment') if recent_trades else None
        }

        if analysis["streak_loss"]:
            print(f"[AI MEMORY] {symbol} has 3+ consecutive losses. Consider reducing lot size or waiting.")
            analysis["adjust_risk"] = True

        return analysis

    def update_strategy(self, symbol):
        analysis = self.analyze_pattern(symbol)
        if analysis.get("adjust_risk"):
            print(f"[STRATEGY UPDATE] Adjusting strategy for {symbol} based on memory.")
            return {"risk_reduction": True}
        return {}

    def summarize_stats(self, symbol):
        trades = self.memory.get(symbol, [])
        total = len(trades)
        wins = sum(1 for t in trades if t.get('profit') is not None and t['profit'] > 0)
        losses = sum(1 for t in trades if t.get('profit') is not None and t['profit'] < 0)
        return {
            "total_trades": total,
            "wins": wins,
            "losses": losses,
            "win_rate": round((wins / total * 100), 2) if total > 0 else 0
        }
