# run_bot.py

from bot_runner import start_bot  # Ensure bot_runner.py is in the same directory or in PYTHONPATH

def main():
    print("📈 Starting Sentinel Forex Bot...")

    try:
        start_bot()  # Starts the threaded bot logic for admin user
    except KeyboardInterrupt:
        print("\n🛑 Bot manually stopped by user.")
    except Exception as e:
        print(f"⚠️ Unexpected error occurred: {e}")
    finally:
        print("🧹 Cleaning up... Exit complete.")

if __name__ == "__main__":
    main()
