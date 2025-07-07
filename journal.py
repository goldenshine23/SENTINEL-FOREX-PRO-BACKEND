import csv
import os
from datetime import datetime, date
from fpdf import FPDF

# === File Paths ===
REPORTS_DIR = "reports"
JOURNAL_CSV = os.path.join(REPORTS_DIR, "trade_journal.csv")
REPORT_PDF = os.path.join(REPORTS_DIR, "daily_report.pdf")


class TradeJournal:
    def __init__(self):
        os.makedirs(REPORTS_DIR, exist_ok=True)
        if not os.path.exists(JOURNAL_CSV):
            with open(JOURNAL_CSV, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Symbol", "EntryPrice", "ExitPrice", "Profit", "Direction"])

    def log_trade(self, symbol, entry_price, exit_price, profit, direction):
        """
        Log a trade to the CSV journal.
        """
        with open(JOURNAL_CSV, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.utcnow().isoformat(),
                symbol,
                round(entry_price, 5),
                round(exit_price, 5) if exit_price is not None else "",
                round(profit, 2) if profit is not None else "",
                direction
            ])

    def export_daily_report(self, report_date: date = None):
        """
        Export trades made on the given date (default: today) into a PDF report.
        """
        if report_date is None:
            report_date = datetime.utcnow().date()

        trades_today = []
        total_profit = 0.0
        wins = 0
        losses = 0

        with open(JOURNAL_CSV, mode="r") as file:
            reader = csv.reader(file)
            headers = next(reader, None)
            for row in reader:
                if len(row) < 6:
                    continue
                try:
                    row_date = datetime.fromisoformat(row[0]).date()
                    if row_date == report_date:
                        trades_today.append(row)
                        profit = float(row[4]) if row[4] else 0
                        total_profit += profit
                        if profit > 0:
                            wins += 1
                        elif profit < 0:
                            losses += 1
                except Exception:
                    continue

        total_trades = len(trades_today)
        win_rate = round((wins / total_trades) * 100, 2) if total_trades else 0.0

        # === Create PDF ===
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Trade Report – {report_date.isoformat()} (UTC)", ln=True, align="C")
        pdf.ln(10)

        if not trades_today:
            pdf.set_font("Arial", size=11)
            pdf.cell(0, 10, "No trades recorded for this day.", ln=True)
        else:
            # Summary
            pdf.set_font("Arial", "B", 11)
            summary = (
                f"Total Trades: {total_trades} | Wins: {wins} | "
                f"Losses: {losses} | Win Rate: {win_rate}% | PnL: {round(total_profit, 2)}"
            )
            pdf.cell(0, 8, summary, ln=True)
            pdf.ln(5)

            # Table header
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 8, " | ".join(headers), ln=True)
            pdf.set_font("Arial", size=10)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(2)

            # Table rows
            for row in trades_today:
                pdf.cell(0, 8, " | ".join(row), ln=True)

        pdf.output(REPORT_PDF)
        return REPORT_PDF
