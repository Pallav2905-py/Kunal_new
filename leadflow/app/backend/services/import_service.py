"""
LeadFlow — Lead Import Service
Handles CSV and Excel import with validation and duplicate detection.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd

from app.backend.models.domain import (
    LeadCreate, LeadSource, ImportValidationResult
)
from app.database.repositories.lead_repo import LeadRepository

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = {"name"}
OPTIONAL_COLUMNS = {"company", "phone", "email", "location", "source", "campaign"}
ALL_COLUMNS = REQUIRED_COLUMNS | OPTIONAL_COLUMNS

# Column name normalizations (allow alternate spellings)
COLUMN_ALIASES = {
    "full_name": "name",
    "fullname": "name",
    "contact_name": "name",
    "organisation": "company",
    "organization": "company",
    "mobile": "phone",
    "phone_number": "phone",
    "telephone": "phone",
    "email_address": "email",
    "city": "location",
    "region": "location",
    "lead_source": "source",
    "utm_campaign": "campaign",
}


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Lowercase and normalize column names."""
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df = df.rename(columns=COLUMN_ALIASES)
    return df


def _parse_row(row: pd.Series, idx: int) -> tuple[LeadCreate | None, str | None]:
    """Parse a single dataframe row into a LeadCreate, returning error if invalid."""
    name = str(row.get("name", "")).strip()
    if not name or name.lower() in ("nan", "none", ""):
        return None, f"Row {idx}: missing required field 'name'"

    phone = str(row.get("phone", "")).strip()
    if phone.lower() in ("nan", "none", ""):
        phone = ""

    email = str(row.get("email", "")).strip().lower()
    if email.lower() in ("nan", "none", ""):
        email = ""

    company = str(row.get("company", "")).strip()
    if company.lower() in ("nan", "none", ""):
        company = ""

    location = str(row.get("location", "")).strip()
    if location.lower() in ("nan", "none", ""):
        location = ""

    source_str = str(row.get("source", "")).strip().lower().replace(" ", "_")
    try:
        source = LeadSource(source_str) if source_str and source_str not in ("nan", "none", "") else LeadSource.IMPORT
    except ValueError:
        source = LeadSource.IMPORT

    campaign = str(row.get("campaign", "")).strip()
    if campaign.lower() in ("nan", "none", ""):
        campaign = ""

    try:
        lead = LeadCreate(
            name=name,
            company=company or None,
            phone=phone or None,
            email=email or None,
            location=location or None,
            source=source,
            campaign=campaign or None,
        )
        return lead, None
    except Exception as e:
        return None, f"Row {idx}: {str(e)}"


class LeadImportService:
    """Service for importing leads from Excel/CSV files."""

    def __init__(self, lead_repo: LeadRepository) -> None:
        self.lead_repo = lead_repo

    def validate_file(self, file_path: str) -> ImportValidationResult:
        """
        Parse and validate a file. Returns detailed validation result
        including valid leads ready for import.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = path.suffix.lower()
        try:
            if ext == ".csv":
                df = pd.read_csv(file_path, dtype=str)
            elif ext in (".xlsx", ".xls"):
                df = pd.read_excel(file_path, dtype=str)
            else:
                raise ValueError(f"Unsupported file format: {ext}. Use .csv or .xlsx")
        except Exception as e:
            raise ValueError(f"Failed to read file: {e}")

        df = _normalize_columns(df)
        df = df.dropna(how="all")  # remove completely empty rows

        if "name" not in df.columns:
            raise ValueError(
                "Missing required column 'name'. "
                f"Found columns: {list(df.columns)}"
            )

        total = len(df)
        valid_leads: list[LeadCreate] = []
        errors: list[dict[str, Any]] = []
        duplicate_count = 0

        for idx, (_, row) in enumerate(df.iterrows(), start=2):
            lead, error = _parse_row(row, idx)
            if error:
                errors.append({"row": idx, "error": error})
                continue

            if lead is None:
                continue

            # Duplicate check against existing database
            if self.lead_repo.exists_by_phone_or_email(lead.phone, lead.email):
                duplicate_count += 1
                errors.append({
                    "row": idx,
                    "error": f"Duplicate lead (phone/email already exists): {lead.name}"
                })
                continue

            valid_leads.append(lead)

        return ImportValidationResult(
            total=total,
            valid=len(valid_leads),
            duplicates=duplicate_count,
            invalid=total - len(valid_leads) - duplicate_count,
            errors=errors,
            valid_leads=valid_leads,
        )

    def import_leads(
        self,
        valid_leads: list[LeadCreate],
        assigned_to: str | None = None,
        assigned_to_name: str | None = None,
    ) -> int:
        """
        Insert validated leads into MongoDB.
        Returns count of successfully imported leads.
        """
        from app.backend.models.domain import LeadDB
        db_leads = []
        for lead in valid_leads:
            db_lead = LeadDB(
                name=lead.name,
                company=lead.company,
                phone=lead.phone,
                email=lead.email,
                location=lead.location,
                source=lead.source,
                campaign=lead.campaign,
                assigned_to=assigned_to,
                assigned_to_name=assigned_to_name,
            )
            db_leads.append(db_lead)

        count = self.lead_repo.create_many(db_leads)
        logger.info(f"Imported {count} leads")
        return count
