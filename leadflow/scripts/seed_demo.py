"""
LeadFlow — Demo Data Seeder
Seeds realistic fictional data for demonstration purposes.
Run: python scripts/seed_demo.py
"""

from __future__ import annotations

import sys
import random
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.database.mongodb import MongoDB
from app.database.repositories.user_repo import UserRepository
from app.database.repositories.lead_repo import LeadRepository
from app.database.repositories.call_repo import CallRepository
from app.database.repositories.followup_repo import FollowUpRepository
from app.backend.services.auth_service import hash_password
from app.backend.models.domain import (
    UserDB, UserRole, LeadDB, LeadStatus, LeadPriority, LeadSource,
    CallRecordDB, CallAnalysisDB, CallAnalysis, CallIntent, CallSentiment,
    FollowUpDB, FollowUpStatus, AnalysisStatus,
)

# ─────────────────────────────────────────────
# DEMO USER DATA
# ─────────────────────────────────────────────

DEMO_USERS = [
    {"name": "Arjun Mehta", "email": "admin@leadflow.local", "role": UserRole.ADMIN, "password": "admin123"},
    {"name": "Priya Sharma", "email": "manager@leadflow.local", "role": UserRole.SALES_MANAGER, "password": "manager123"},
    {"name": "Rahul Kumar", "email": "rahul@leadflow.local", "role": UserRole.SALES_EXECUTIVE, "password": "exec123"},
    {"name": "Sneha Patel", "email": "sneha@leadflow.local", "role": UserRole.SALES_EXECUTIVE, "password": "exec123"},
    {"name": "Vikram Nair", "email": "vikram@leadflow.local", "role": UserRole.SALES_EXECUTIVE, "password": "exec123"},
    {"name": "Ananya Singh", "email": "ananya@leadflow.local", "role": UserRole.SALES_EXECUTIVE, "password": "exec123"},
    {"name": "Karan Joshi", "email": "karan@leadflow.local", "role": UserRole.SALES_EXECUTIVE, "password": "exec123"},
    {"name": "Support Staff", "email": "support@leadflow.local", "role": UserRole.SUPPORT, "password": "support123"},
]

COMPANIES = [
    "TechSolutions Pvt Ltd", "Innovate Systems", "Global Ventures", "NextGen Corp",
    "DataDrive Ltd", "CloudFirst Technologies", "Apex Software", "Horizon Enterprises",
    "Synergy Group", "Pinnacle Solutions", "BlueSky Analytics", "CoreLogic Systems",
    "Digital Frontiers", "Momentum Tech", "Vector Industries", "Cascade Networks",
    "Paramount Software", "Genesis Technologies", "Frontier Dynamics", "Stellar Corp",
    "Quantum Leap Pvt", "Nexus Enterprises", "Meridian Solutions", "Apex Digital",
    "Omega Technologies", "Prism Analytics", "Echo Systems", "Vertex Solutions",
    "Catalyst Tech", "Fusion Labs",
]

LEAD_NAMES = [
    "Rahul Sharma", "Priya Singh", "Amit Patel", "Sunita Gupta", "Ravi Kumar",
    "Neha Verma", "Arun Mehta", "Kavita Nair", "Suresh Rao", "Divya Bose",
    "Manish Jain", "Pooja Agarwal", "Deepak Tiwari", "Anjali Mishra", "Vikas Yadav",
    "Rekha Pandey", "Sanjay Dubey", "Meera Pillai", "Rajesh Kapoor", "Swetha Reddy",
    "Harish Chandra", "Geetha Krishnan", "Mohan Das", "Lakshmi Iyer", "Siddharth Roy",
    "Nandita Chatterjee", "Ashok Bhatt", "Usha Rani", "Ganesh Moorthy", "Varsha Shah",
    "Manoj Sinha", "Kamla Devi", "Prakash Nayak", "Sarla Joshi", "Devendra Singh",
    "Mala Srivastava", "Vinod Bhatia", "Sushma Tyagi", "Girish Saxena", "Anita Chopra",
    "Naresh Kumar", "Hema Malhotra", "Sunil Aggarwal", "Padma Iyengar", "Satish Chandra",
    "Uma Shankar", "Tapan Ghosh", "Chetna Banerjee", "Ratan Dey", "Archana Pillai",
    "Kiran Bedi", "Sundar Rajan", "Leela Krishnan", "Murali Mohan", "Shanthi Kumari",
    "Vivek Anand", "Deepika Goyal", "Subramaniam M", "Shakuntala Devi", "Ramesh Balaji",
    "Nalini Subramanian", "Prem Kumar", "Sarita Acharya", "Monika Sood", "Yusuf Khan",
    "Faiza Ansari", "Imran Sheikh", "Nadia Begum", "Tariq Ahmad", "Rubina Parveen",
    "Samuel Johnson", "Aniket Desai", "Shweta Kulkarni", "Nilesh Bhosle", "Tejal Pawar",
]

SOURCES = list(LeadSource)
LOCATIONS = [
    "Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Kolkata", "Pune",
    "Ahmedabad", "Jaipur", "Lucknow", "Surat", "Kochi", "Chandigarh", "Bhopal", "Nagpur",
]
CAMPAIGNS = [
    "Q4 Enterprise Drive", "Digital Transformation Campaign", "SMB Outreach Q1",
    "Product Launch 2024", "Cloud Migration Initiative", "Year-End Deals",
    None, None, None,  # Some leads with no campaign
]

REQUIREMENTS_POOL = [
    "CRM integration with existing ERP",
    "Custom reporting dashboard",
    "Mobile application access",
    "Multi-user licensing",
    "On-premise deployment option",
    "API access for third-party tools",
    "Data migration from current system",
    "Training and onboarding support",
    "SLA and support contract",
    "GDPR compliance features",
    "SSO integration",
    "Advanced analytics module",
    "Bulk data import capability",
    "Automated email workflows",
    "Real-time notifications",
]

OBJECTIONS_POOL = [
    "Pricing is too high compared to budget",
    "Need approval from management before proceeding",
    "Currently under contract with a competitor",
    "Concerned about implementation timeline",
    "Unsure about ROI",
    "Need more time to evaluate options",
    "Internal resource constraints",
    "Security and compliance concerns",
    "Feature gaps compared to current solution",
    "Wants a longer trial period",
]

SUMMARIES_POSITIVE = [
    "Customer expressed strong interest in the enterprise plan. They require CRM integration and advanced analytics. Purchase decision expected within 30 days. Requested a detailed proposal.",
    "Prospect demonstrated high purchase intent. They have a clear requirement for cloud-based deployment serving 200+ users. Budget has been approved internally.",
    "Engaging conversation where customer confirmed interest in migrating from their legacy system. They liked the demo and are scheduling an internal review meeting.",
    "Customer confirmed budget availability and decision authority. They want implementation within Q1. Follow-up demo scheduled.",
    "Strong buying signal detected. Customer compared our solution favorably to competitors and requested pricing for the 500-user enterprise tier.",
]

SUMMARIES_NEUTRAL = [
    "Initial discovery call. Customer is evaluating multiple vendors. They showed interest in the product but have not committed to any timeline yet.",
    "Customer requested more information about pricing and deployment options. They are in early evaluation stage and will share details with their IT team.",
    "Exploratory call with IT manager. They acknowledged a need for better lead management but are awaiting budget approval for next quarter.",
    "Customer inquired about specific compliance features. Overall positive, but needs internal sign-off before progressing.",
    "Discovery call with procurement team. They are building a shortlist and will schedule a formal demo next week.",
]

SUMMARIES_NEGATIVE = [
    "Customer expressed concern about high pricing and indicated the current budget does not accommodate the enterprise tier. Negotiation required.",
    "Customer is currently under a 12-month contract with a competitor and cannot switch before Q3. Keeping in pipeline for future consideration.",
    "Conversation revealed misalignment of product features with customer's specific workflow requirements. Customer was polite but not interested.",
    "Customer cited budget constraints and does not see the implementation ROI within their current planning cycle.",
]


def random_phone() -> str:
    return f"+91 {random.randint(70000, 99999):05d} {random.randint(10000, 99999):05d}"


def random_email(name: str) -> str:
    first = name.split()[0].lower()
    domain = random.choice(["gmail.com", "company.in", "business.com", "corp.net", "mail.com"])
    return f"{first}.{random.randint(10, 99)}@{domain}"


def seed_users(repo: UserRepository) -> list[UserDB]:
    users = []
    for u in DEMO_USERS:
        existing = repo.find_by_email(u["email"])
        if existing:
            users.append(existing)
            continue
        user = UserDB(
            name=u["name"],
            email=u["email"],
            password_hash=hash_password(u["password"]),
            role=u["role"],
            is_active=True,
        )
        users.append(repo.create(user))
    print(f"✓ {len(users)} users seeded")
    return users


def seed_leads(repo: LeadRepository, executives: list[UserDB]) -> list[LeadDB]:
    leads = []
    used_names = set()
    random.shuffle(LEAD_NAMES)

    statuses = [
        LeadStatus.NEW, LeadStatus.CONTACTED, LeadStatus.INTERESTED,
        LeadStatus.FOLLOW_UP, LeadStatus.NEGOTIATION,
        LeadStatus.CONVERTED, LeadStatus.LOST,
    ]
    status_weights = [15, 20, 25, 15, 10, 10, 5]

    for i, name in enumerate(LEAD_NAMES[:75]):
        if name in used_names:
            continue
        used_names.add(name)

        company = COMPANIES[i % len(COMPANIES)]
        exec_user = random.choice(executives)
        status = random.choices(statuses, weights=status_weights)[0]
        score = random.randint(20, 100)

        if score >= 70:
            priority = LeadPriority.HIGH
        elif score >= 40:
            priority = LeadPriority.MEDIUM
        else:
            priority = LeadPriority.LOW

        # Sentiment hint based on status
        if status in (LeadStatus.INTERESTED, LeadStatus.CONVERTED, LeadStatus.NEGOTIATION):
            sentiment = random.choice(["POSITIVE", "MIXED"])
        elif status == LeadStatus.LOST:
            sentiment = random.choice(["NEGATIVE", "NEUTRAL"])
        else:
            sentiment = random.choice(["POSITIVE", "NEUTRAL", "NEGATIVE", "MIXED"])

        intent_map = {
            LeadStatus.INTERESTED: CallIntent.PURCHASE,
            LeadStatus.NEGOTIATION: CallIntent.NEGOTIATION,
            LeadStatus.CONVERTED: CallIntent.PURCHASE,
            LeadStatus.LOST: CallIntent.NOT_INTERESTED,
            LeadStatus.CONTACTED: CallIntent.INQUIRY,
            LeadStatus.NEW: CallIntent.UNKNOWN,
            LeadStatus.FOLLOW_UP: CallIntent.FOLLOW_UP,
        }
        intent = intent_map.get(status, CallIntent.UNKNOWN)

        created_ago = timedelta(days=random.randint(1, 90))
        last_contact = datetime.utcnow() - timedelta(days=random.randint(1, 30)) if status != LeadStatus.NEW else None
        next_followup = datetime.utcnow() + timedelta(days=random.randint(1, 14)) if status in (
            LeadStatus.FOLLOW_UP, LeadStatus.INTERESTED, LeadStatus.NEGOTIATION
        ) else None

        summary_pool = SUMMARIES_POSITIVE if sentiment == "POSITIVE" else (
            SUMMARIES_NEGATIVE if sentiment == "NEGATIVE" else SUMMARIES_NEUTRAL
        )

        lead = LeadDB(
            name=name,
            company=company,
            phone=random_phone(),
            email=random_email(name),
            location=random.choice(LOCATIONS),
            source=random.choice(SOURCES),
            campaign=random.choice(CAMPAIGNS),
            status=status,
            priority=priority,
            lead_score=score,
            assigned_to=exec_user.id,
            assigned_to_name=exec_user.name,
            intent=intent.value,
            sentiment=sentiment,
            requirements=random.sample(REQUIREMENTS_POOL, random.randint(0, 3)),
            objections=random.sample(OBJECTIONS_POOL, random.randint(0, 2)),
            ai_summary=random.choice(summary_pool) if random.random() > 0.3 else None,
            created_at=datetime.utcnow() - created_ago,
            last_contact=last_contact,
            next_followup=next_followup,
        )
        leads.append(repo.create(lead))

    print(f"✓ {len(leads)} leads seeded")
    return leads


def seed_calls_and_analyses(
    call_repo: CallRepository,
    lead_repo: LeadRepository,
    leads: list[LeadDB],
    executives: list[UserDB],
):
    """Seed call records and analyses for leads that have contact history."""
    analysis_leads = [
        l for l in leads
        if l.status.value in ("contacted", "interested", "follow_up", "negotiation", "converted", "lost")
    ][:25]

    count = 0
    for lead in analysis_leads:
        sentiment = lead.sentiment or "NEUTRAL"
        score = lead.lead_score

        if score >= 70:
            priority = LeadPriority.HIGH
        elif score >= 40:
            priority = LeadPriority.MEDIUM
        else:
            priority = LeadPriority.LOW

        intent_map = {
            "interested": CallIntent.PURCHASE,
            "negotiation": CallIntent.NEGOTIATION,
            "converted": CallIntent.PURCHASE,
            "lost": CallIntent.NOT_INTERESTED,
            "contacted": CallIntent.INQUIRY,
            "follow_up": CallIntent.FOLLOW_UP,
        }
        intent = intent_map.get(lead.status.value, CallIntent.INQUIRY)

        sentiment_enum = CallSentiment(sentiment)
        exec_user = random.choice(executives)
        created_at = datetime.utcnow() - timedelta(days=random.randint(1, 30))

        record = CallRecordDB(
            lead_id=lead.id,
            lead_name=lead.name,
            file_path=f"uploads/recordings/demo_{count}.wav",
            file_name=f"call_{lead.name.replace(' ', '_').lower()}.wav",
            file_size_bytes=random.randint(500000, 5000000),
            duration_seconds=random.uniform(120, 1200),
            analysis_status=AnalysisStatus.COMPLETED,
            uploaded_by=exec_user.id,
            uploaded_by_name=exec_user.name,
            created_at=created_at,
            transcribed_at=created_at + timedelta(minutes=1),
            analyzed_at=created_at + timedelta(minutes=2),
        )

        summary_pool = SUMMARIES_POSITIVE if sentiment == "POSITIVE" else (
            SUMMARIES_NEGATIVE if sentiment == "NEGATIVE" else SUMMARIES_NEUTRAL
        )
        summary = random.choice(summary_pool)

        record.transcript = (
            f"Sales Executive: Hello {lead.name}, how are you today?\n"
            f"Customer: Good, thanks. I was looking at your CRM solution.\n"
            f"Sales Executive: Great! What specific features are you looking for?\n"
            f"Customer: We need {', '.join(lead.requirements[:2]) if lead.requirements else 'integration and reporting'}.\n"
            f"{'Customer: My main concern is ' + lead.objections[0] + '.' if lead.objections else ''}\n"
            f"Sales Executive: I understand. Let me address that..."
        )

        record = call_repo.create_record(record)

        # Analysis
        analysis = CallAnalysis(
            summary=summary,
            intent=intent,
            sentiment=sentiment_enum,
            requirements=lead.requirements,
            objections=lead.objections,
            purchase_timeline=random.choice([
                "Within 30 days", "Next quarter", "6 months", "End of year", None
            ]),
            lead_score=score,
            priority=priority,
            follow_up_required=lead.status.value in ("follow_up", "interested", "contacted"),
            follow_up_reason="Follow up on proposal" if lead.status.value == "follow_up" else None,
            recommended_action=random.choice([
                "Send detailed product proposal",
                "Schedule technical demo",
                "Follow up with pricing details",
                "Escalate to sales manager",
                "Send case studies",
                "Schedule onboarding call",
            ]),
            confidence=round(random.uniform(0.65, 0.96), 2),
        )

        analysis_db = CallAnalysisDB(
            call_id=record.id,
            lead_id=lead.id,
            analysis=analysis,
            processing_time_seconds=round(random.uniform(3.0, 12.0), 2),
            created_at=created_at + timedelta(minutes=2),
        )
        call_repo.create_analysis(analysis_db)
        count += 1

    print(f"✓ {count} call records and analyses seeded")


def seed_followups(
    repo: FollowUpRepository,
    leads: list[LeadDB],
    executives: list[UserDB],
):
    followup_leads = [
        l for l in leads
        if l.status.value in ("follow_up", "interested", "contacted", "negotiation")
    ][:30]

    count = 0
    for lead in followup_leads:
        exec_user = random.choice(executives)
        days_ahead = random.randint(-5, 14)  # Some overdue, some future
        due_date = datetime.utcnow() + timedelta(days=days_ahead)

        if days_ahead < 0:
            status = FollowUpStatus.OVERDUE
        else:
            status = random.choice([FollowUpStatus.PENDING, FollowUpStatus.PENDING, FollowUpStatus.COMPLETED])

        followup = FollowUpDB(
            lead_id=lead.id,
            lead_name=lead.name,
            reason=random.choice([
                "Send product proposal after initial discussion",
                "Schedule technical demo",
                "Follow up on pricing inquiry",
                "Check decision timeline",
                "Send case studies as requested",
                "Confirm next steps after demo",
                "Follow up on contract review",
            ]),
            due_date=due_date,
            assigned_to=exec_user.id,
            assigned_to_name=exec_user.name,
            priority=lead.priority,
            status=status,
        )
        repo.create(followup)
        count += 1

    print(f"✓ {count} follow-ups seeded")


def main():
    print("LeadFlow Demo Data Seeder")
    print("=" * 40)

    MongoDB.connect(settings.mongodb_uri, settings.database_name)
    db = MongoDB.get_db()

    user_repo = UserRepository(db)
    lead_repo = LeadRepository(db)
    call_repo = CallRepository(db)
    followup_repo = FollowUpRepository(db)

    # Ask before clearing
    existing_leads = lead_repo.count_total()
    if existing_leads > 0:
        response = input(f"Database has {existing_leads} leads. Clear and reseed? [y/N]: ")
        if response.lower() != "y":
            print("Seeding cancelled.")
            MongoDB.disconnect()
            return

        # Clear collections
        db.leads.delete_many({})
        db.call_records.delete_many({})
        db.call_analyses.delete_many({})
        db.follow_ups.delete_many({})
        print("✓ Collections cleared")

    # Seed
    users = seed_users(user_repo)
    executives = [u for u in users if u.role in (UserRole.SALES_EXECUTIVE, UserRole.SALES_MANAGER)]

    leads = seed_leads(lead_repo, executives)
    seed_calls_and_analyses(call_repo, lead_repo, leads, executives)
    seed_followups(followup_repo, leads, executives)

    MongoDB.disconnect()

    print()
    print("=" * 40)
    print("Demo data seeded successfully!")
    print()
    print("Login credentials:")
    for u in DEMO_USERS:
        print(f"  {u['role'].value:25s}  {u['email']:35s}  password: {u['password']}")


if __name__ == "__main__":
    main()
