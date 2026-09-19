import random
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from app.config import settings
# ---------- CONFIG ----------


NUM_VENDORS = 75
AUDITS_PER_VENDOR = 2
NUM_RETENTION = 60
NUM_REVIEWS = 60

random.seed(42)
# ----------------------------

@contextmanager
def get_conn():
    conn = sqlite3.connect(
        settings.DB_FILE
    )

    conn.row_factory = sqlite3.Row

    try:
        yield conn
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def random_date(start_year=2023, end_year=2026):
    start = datetime(start_year, 1, 1, tzinfo=timezone.utc)
    end = datetime(end_year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
    random_dt = start + timedelta(days=random.randint(0, (end - start).days))
    return random_dt.strftime("%Y-%m-%d %H:%M:%S")

def risk_category(score):
    if score >= 85:
        return "Critical"
    elif score >= 70:
        return "High"
    elif score >= 50:
        return "Medium"
    else:
        return "Low"

def severity_from_risk(score):
    if score >= 85:
        return random.choice(["High", "Critical"])
    elif score >= 70:
        return random.choice(["Medium", "High"])
    elif score >= 50:
        return "Medium"
    else:
        return "Low"

def init_db(cur):
    """Creates tables if they do not already exist in SQLite."""
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                name TEXT,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );""")
    cur.execute("""CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                thread_id TEXT NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY(username) REFERENCES users(username)
            );""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS vendors (
        vendor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_name TEXT,
        risk_score INTEGER,
        risk_category TEXT,
        compliance_status TEXT,
        approval_status TEXT,
        onboarding_date TEXT,
        last_audit_date TEXT,
        next_review_due TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_id INTEGER,
        policy_reference TEXT,
        issue_title TEXT,
        issue_severity TEXT,
        remediation_status TEXT,
        issue_identified_date TEXT,
        target_resolution_date TEXT,
        resolution_date TEXT,
        escalation_flag INTEGER,
        FOREIGN KEY (vendor_id) REFERENCES vendors (vendor_id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS retention_records (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        department TEXT,
        vendor_id INTEGER,
        data_category TEXT,
        retention_period_years INTEGER,
        legal_hold_flag INTEGER,
        approval_status TEXT,
        last_review_date TEXT,
        next_review_due TEXT,
        FOREIGN KEY (vendor_id) REFERENCES vendors (vendor_id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS compliance_reviews (
        review_id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_id INTEGER,
        reviewer_name TEXT,
        review_type TEXT,
        review_status TEXT,
        review_notes TEXT,
        review_date TEXT,
        next_review_due TEXT,
        FOREIGN KEY (vendor_id) REFERENCES vendors (vendor_id)
    );
    """)

def main():
    with get_conn() as conn:
        cur = conn.cursor()

        # Create schema tables
        init_db(cur)

        vendor_ids = []

        # -------- Vendors --------
        for i in range(NUM_VENDORS):
            score = random.randint(40, 95)
            category = risk_category(score)

            cur.execute("""
            INSERT INTO vendors (
                vendor_name, risk_score, risk_category, compliance_status,
                approval_status, onboarding_date, last_audit_date, next_review_due
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"Vendor_{i}",
                score,
                category,
                random.choice(["Compliant", "Under Review", "Non-Compliant"]),
                random.choice(["Approved", "Pending", "Rejected"]),
                random_date(2022, 2024),
                random_date(2024, 2025),
                random_date(2025, 2026)
            ))

            vendor_ids.append(cur.lastrowid)

        # -------- Audit Logs --------
        for vid in vendor_ids:
            for _ in range(AUDITS_PER_VENDOR):
                score = random.randint(40, 95)
                severity = severity_from_risk(score)

                identified_str = random_date(2024, 2025)
                identified = datetime.strptime(identified_str, "%Y-%m-%d %H:%M:%S").astimezone(timezone.utc)
                
                target_dt = identified + timedelta(days=random.randint(15, 60))
                target_str = target_dt.strftime("%Y-%m-%d %H:%M:%S")
                resolved_str = None

                remediation_status = random.choice(["Open", "In Progress", "Closed"])

                if remediation_status == "Closed":
                    resolved_dt = target_dt - timedelta(days=random.randint(1, 10))
                    resolved_str = resolved_dt.strftime("%Y-%m-%d %H:%M:%S")

                escalation = int(remediation_status != "Closed" and datetime.now(tz=timezone.utc) > target_dt)

                cur.execute("""
                INSERT INTO audit_logs (
                    vendor_id, policy_reference, issue_title, issue_severity,
                    remediation_status, issue_identified_date, target_resolution_date,
                    resolution_date, escalation_flag
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    vid,
                    random.choice([
                        "Vendor Compliance Policy",
                        "Data Retention Policy",
                        "Access Control Policy",
                        "Anti-Bribery Policy"
                    ]),
                    "Generated Compliance Finding",
                    severity,
                    remediation_status,
                    identified_str,
                    target_str,
                    resolved_str,
                    escalation
                ))

        # -------- Retention Records --------
        for _ in range(NUM_RETENTION):
            cur.execute("""
            INSERT INTO retention_records (
                department, vendor_id, data_category, retention_period_years,
                legal_hold_flag, approval_status, last_review_date, next_review_due
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                random.choice(["Finance", "Marketing", "HR", "IT", "Legal"]),
                random.choice(vendor_ids),
                random.choice([
                    "Transaction Records",
                    "Customer Email Data",
                    "Employee Records",
                    "Security Logs",
                    "Contract Documents"
                ]),
                random.randint(2, 10),
                int(random.choice([True, False])),
                random.choice(["Approved", "Pending"]),
                random_date(2024, 2025),
                random_date(2025, 2026)
            ))

        # -------- Compliance Reviews --------
        for _ in range(NUM_REVIEWS):
            cur.execute("""
            INSERT INTO compliance_reviews (
                vendor_id, reviewer_name, review_type, review_status,
                review_notes, review_date, next_review_due
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                random.choice(vendor_ids),
                random.choice(["Anita Sharma", "Rahul Mehta", "Priya Iyer", "Arjun Rao"]),
                random.choice(["Quarterly Review", "Annual Certification", "Escalation Review"]),
                random.choice(["Open", "Closed", "In Progress"]),
                "Synthetic generated review",
                random_date(2024, 2025),
                random_date(2025, 2026)
            ))

    # conn.commit()
    # cur.close()
    # conn.close()

    print("SQLite Capstone dataset generated successfully in 'retail_compliance.db'.")

if __name__ == "__main__":
    main()