"""
Flask web dashboard for FlowVello Gmail Agent.
"""
from flask import Flask, render_template, request, redirect, url_for, flash
from config import config
from gmail_agent.database import Database
from gmail_agent.auth import is_authenticated
from gmail_agent.scheduler import EmailScheduler

app = Flask(__name__)
app.secret_key = config.FLASK_SECRET_KEY
db = Database()
scheduler = EmailScheduler()


@app.context_processor
def inject_globals():
    return {
        "pending_drafts_count": len(db.get_pending_drafts()),
        "gmail_status": "Connected" if is_authenticated() else "Not connected",
    }


@app.route("/")
def dashboard():
    stats = [
        {"label": "Emails", "value": db.get_totals().get("total_emails", 0), "sub": "Total processed"},
        {"label": "Leads", "value": db.get_totals().get("total_leads", 0), "sub": "Captured"},
        {"label": "Drafts", "value": db.get_totals().get("total_drafts", 0), "sub": "AI generated"},
        {"label": "Sent", "value": db.get_totals().get("sent_count", 0), "sub": "Replies sent"},
        {"label": "Follow-ups", "value": db.get_totals().get("active_followups", 0), "sub": "Active sequences"},
    ]
    recent = db.get_all_emails(limit=10)
    pending = db.get_pending_drafts()
    return render_template("dashboard.html", stats=stats, recent_emails=recent,
                           pending_drafts=pending, active="dashboard")


@app.route("/inbox")
def inbox():
    filter_type = request.args.get("filter", "all")
    emails = db.get_all_emails(limit=50)
    
    if filter_type == "lead":
        emails = [e for e in emails if e.get("is_lead")]
    elif filter_type == "urgent":
        emails = [e for e in emails if e.get("priority") in ("urgent", "high")]
    elif filter_type == "support":
        emails = [e for e in emails if e.get("intent") == "client_support"]
    
    return render_template("inbox.html", emails=emails, filter=filter_type, active="inbox")


@app.route("/email/<email_id>")
def email_detail(email_id):
    email = db.get_email_by_id(email_id)
    if not email:
        flash("Email not found", "error")
        return redirect(url_for("inbox"))
    return render_template("email_detail.html", email=email, active="inbox")


@app.route("/drafts")
def drafts():
    pending = db.get_pending_drafts()
    return render_template("drafts.html", drafts=pending, active="drafts")


@app.route("/draft/<int:draft_id>/approve", methods=["POST"])
def approve_draft(draft_id):
    from gmail_agent.gmail_service import send_email
    from gmail_agent.database import Database
    db_local = Database()
    
    # Get the draft
    drafts = db_local.get_pending_drafts()
    draft = next((d for d in drafts if d["id"] == draft_id), None)
    
    if draft:
        body_to_send = draft.get("edited_body") or draft["body"]
        success = send_email(
            to=draft["from_address"],
            subject=draft["subject"],
            body=body_to_send,
        )
        if success:
            db_local.update_draft_status(draft_id, "sent", body_to_send)
            db_local.increment_analytics(__import__("datetime").datetime.now().strftime("%Y-%m-%d"), "drafts_approved")
            flash("✅ Draft approved and sent!", "success")
        else:
            flash("❌ Failed to send email", "error")
    else:
        flash("Draft not found", "error")
    
    return redirect(url_for("drafts"))


@app.route("/draft/<int:draft_id>/reject", methods=["POST"])
def reject_draft(draft_id):
    db.update_draft_status(draft_id, "rejected")
    flash("Draft rejected", "info")
    return redirect(url_for("drafts"))


@app.route("/leads")
def leads():
    all_leads = db.get_all_leads()
    return render_template("leads.html", leads=all_leads, active="leads")


@app.route("/followups")
def followups():
    fups = db.get_active_followups()
    return render_template("followups.html", followups=fups, active="followups")


@app.route("/analytics")
def analytics():
    totals = db.get_totals()
    daily = db.get_analytics(days=30)
    return render_template("analytics.html", totals=totals, daily=daily, active="analytics")


@app.route("/scan")
def scan_inbox():
    count = scheduler.process_new_emails()
    flash(f"✅ Scanned inbox: {count} new emails processed", "success")
    return redirect(url_for("dashboard"))


def run_dashboard(host="0.0.0.0", port=None, debug=None):
    """Run the Flask web dashboard."""
    port = port or config.FLASK_PORT
    debug = debug if debug is not None else config.FLASK_DEBUG
    app.run(host=host, port=port, debug=debug)
