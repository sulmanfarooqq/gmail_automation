#!/usr/bin/env python3
"""
FlowVello Gmail AI Agent — Main Entry Point

Usage:
    python main.py --mode web        # Web dashboard
    python main.py --mode scan       # One-time inbox scan
    python main.py --mode watch      # Continuous monitoring
    python main.py --mode auth       # Set up Gmail OAuth
    python main.py --mode summary    # Generate daily summary
"""
import sys
import argparse
from config import config
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="FlowVello Gmail AI Agent")
    parser.add_argument("--mode", choices=["web", "scan", "watch", "auth", "summary"],
                        default="web", help="Operation mode")
    parser.add_argument("--port", type=int, default=config.FLASK_PORT,
                        help="Web dashboard port")
    parser.add_argument("--interval", type=int, default=config.SCAN_INTERVAL_MINUTES,
                        help="Scan interval in minutes (watch mode)")
    args = parser.parse_args()

    # Ensure data directories exist
    Path(config.DATA_DIR).mkdir(parents=True, exist_ok=True)
    Path(config.TOKEN_DIR).mkdir(parents=True, exist_ok=True)

    if args.mode == "auth":
        _setup_auth()
    elif args.mode == "scan":
        _run_scan()
    elif args.mode == "watch":
        _run_watch(args.interval)
    elif args.mode == "summary":
        _run_summary()
    elif args.mode == "web":
        _run_web(args.port)


def _setup_auth():
    """Set up Gmail OAuth authentication."""
    from gmail_agent.auth import get_gmail_service
    print("🔐 Setting up Gmail OAuth...")
    print("   A browser window will open. Sign in with flowvello's Gmail.")
    print("   Grant the requested permissions.\n")
    try:
        service = get_gmail_service()
        profile = service.users().getProfile(userId="me").execute()
        print(f"\n✅ Connected to: {profile.get('emailAddress', 'Unknown')}")
        print(f"   Total messages: {profile.get('messagesTotal', 0)}")
        print(f"   Threads: {profile.get('threadsTotal', 0)}")
    except Exception as e:
        print(f"\n❌ Authentication failed: {e}")
        print("\nMake sure credentials.json is in the project root.")
        print("Download it from: Google Cloud Console → APIs & Services → Credentials")


def _run_scan():
    """Run a one-time inbox scan and process emails."""
    from gmail_agent.scheduler import EmailScheduler
    print("🔍 Scanning inbox...")
    scheduler = EmailScheduler()
    count = scheduler.process_new_emails()
    print(f"\n✅ Done. Processed {count} emails.")
    
    # Show stats
    from gmail_agent.database import Database
    db = Database()
    totals = db.get_totals()
    print(f"\n📊 Stats:")
    print(f"   Total emails stored: {totals.get('total_emails', 0)}")
    print(f"   Total leads: {totals.get('total_leads', 0)}")
    print(f"   Pending drafts: {len(db.get_pending_drafts())}")


def _run_watch(interval: int):
    """Run continuous email monitoring."""
    from gmail_agent.scheduler import EmailScheduler
    scheduler = EmailScheduler()
    print(f"👀 Watching inbox (scan every {interval} minutes)")
    print("   Press Ctrl+C to stop\n")
    try:
        scheduler.run_continuous(interval_minutes=interval)
    except KeyboardInterrupt:
        print("\n\n👋 Stopped.")


def _run_summary():
    """Generate and display daily summary."""
    from gmail_agent.scheduler import EmailScheduler
    scheduler = EmailScheduler()
    scheduler.generate_daily_summary()


def _run_web(port: int):
    """Start the web dashboard."""
    print(f"🌐 Starting FlowVello Dashboard at http://localhost:{port}")
    print(f"   Open your browser and navigate there.")
    from dashboard.web import run_dashboard
    run_dashboard(port=port)


if __name__ == "__main__":
    main()
