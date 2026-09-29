"""
Generate a sample leads Excel file for import demo.
Run: python3 scripts/create_sample_import.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd

SAMPLE_DATA = [
    {"name": "Suresh Menon", "company": "Apex Tech Pvt Ltd", "phone": "+91 90001 11111", "email": "suresh@apextech.in", "location": "Bangalore", "source": "website", "campaign": "Q4 Enterprise Drive"},
    {"name": "Kavitha Reddy", "company": "Horizon Systems", "phone": "+91 90001 22222", "email": "kavitha@horizon.com", "location": "Hyderabad", "source": "linkedin", "campaign": "Digital Transformation"},
    {"name": "Rajan Pillai", "company": "NextGen Corp", "phone": "+91 90001 33333", "email": "rajan@nextgen.co.in", "location": "Chennai", "source": "referral", "campaign": None},
    {"name": "Meena Krishnan", "company": "DataPro Solutions", "phone": "+91 90001 44444", "email": "meena@datapro.com", "location": "Mumbai", "source": "email_campaign", "campaign": "SMB Outreach"},
    {"name": "Alok Sharma", "company": "CloudFirst Ltd", "phone": "+91 90001 55555", "email": "alok@cloudfirst.in", "location": "Delhi", "source": "cold_call", "campaign": None},
    {"name": "Nisha Gupta", "company": "TechVision Pvt", "phone": "+91 90001 66666", "email": "nisha@techvision.com", "location": "Pune", "source": "trade_show", "campaign": "Product Launch"},
    {"name": "Vijay Kumar", "company": "Synergy Group", "phone": "+91 90001 77777", "email": "vijay@synergy.in", "location": "Ahmedabad", "source": "partner", "campaign": None},
    {"name": "Priti Jain", "company": "Momentum Tech", "phone": "+91 90001 88888", "email": "priti@momentum.com", "location": "Jaipur", "source": "website", "campaign": "Q4 Enterprise Drive"},
    {"name": "Santhosh Kumar", "company": "Vector Industries", "phone": "+91 90001 99999", "email": "santhosh@vector.co", "location": "Kochi", "source": "linkedin", "campaign": None},
    {"name": "Deepika Nair", "company": "Cascade Networks", "phone": "+91 90002 10000", "email": "deepika@cascade.net", "location": "Kolkata", "source": "referral", "campaign": "Year-End Deals"},
    # Invalid row (missing name) — to demonstrate validation
    {"name": "", "company": "Bad Corp", "phone": "+91 90000 00001", "email": "bad@corp.com", "location": "Unknown", "source": "website", "campaign": None},
    # Duplicate of first row — to demonstrate duplicate detection
    {"name": "Suresh Menon Duplicate", "company": "Apex Tech", "phone": "+91 90001 11111", "email": "suresh@apextech.in", "location": "Bangalore", "source": "website", "campaign": None},
]

if __name__ == "__main__":
    df = pd.DataFrame(SAMPLE_DATA)
    output = Path("sample_leads.xlsx")
    df.to_excel(str(output), index=False)
    print(f"Sample leads file created: {output}")
    print(f"  Total rows: {len(df)}")
    print(f"  1 invalid row (empty name)")
    print(f"  1 potential duplicate (same phone/email)")
    print(f"  ~10 valid leads ready to import")
