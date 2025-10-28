import pandas as pd
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from campaigns.models import Recipient


def import_recipients_from_file(file):
    """
    Reads CSV or Excel file, validates data, and performs bulk insert.
    Returns summary with inserted and skipped records.
    """

    # Determine file type
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    elif file.name.endswith(".xlsx"):
        df = pd.read_excel(file)
    else:
        raise ValueError("Unsupported file format")

    required_columns = {"name", "email"}
    if not required_columns.issubset(df.columns.str.lower()):
        raise ValueError(f"File must contain columns: {required_columns}")

    # Normalize columns
    df.columns = df.columns.str.lower()
    df = df[["name", "email"]]

    inserted = 0
    skipped = 0
    errors = []

    # Clean and validate records
    recipients_to_create = []
    seen_emails = set()
    existing_emails = set(Recipient.objects.values_list("email", flat=True))

    for _, row in df.iterrows():
        name = str(row.get("name", "")).strip()
        email = str(row.get("email", "")).strip()

        # Validation checks
        if not name or not email:
            errors.append({"email": email, "reason": "Missing name or email"})
            skipped += 1
            continue

        try:
            validate_email(email)
        except ValidationError:
            errors.append({"email": email, "reason": "Invalid email format"})
            skipped += 1
            continue

        # Skip duplicates (in file or DB)
        if email in seen_emails or email in existing_emails:
            errors.append({"email": email, "reason": "Duplicate email"})
            skipped += 1
            continue

        seen_emails.add(email)

        recipients_to_create.append(
            Recipient(name=name, email=email, subscription_status="subscribed")
        )

    # Bulk insert for efficiency
    if recipients_to_create:
        Recipient.objects.bulk_create(recipients_to_create, ignore_conflicts=True)
        inserted = len(recipients_to_create)

    return {
        "inserted": inserted,
        "skipped": skipped,
        "errors": errors[:10],  # Return only first 10 for brevity
        "total": len(df),
    }
