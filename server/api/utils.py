"""
Utility functions for Blood Donation System.
"""

# Blood type compatibility matrix
# Key = recipient blood type, Value = list of compatible donor types
BLOOD_COMPATIBILITY = {
    'A+': ['A+', 'A-', 'O+', 'O-'],
    'A-': ['A-', 'O-'],
    'B+': ['B+', 'B-', 'O+', 'O-'],
    'B-': ['B-', 'O-'],
    'AB+': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],  # Universal recipient
    'AB-': ['A-', 'B-', 'AB-', 'O-'],
    'O+': ['O+', 'O-'],
    'O-': ['O-'],  # Universal donor
}


def get_compatible_donors(recipient_blood_group):
    """Return list of blood groups that can donate to the given recipient."""
    return BLOOD_COMPATIBILITY.get(recipient_blood_group, [])


def get_compatible_recipients(donor_blood_group):
    """Return list of blood groups that the given donor can donate to."""
    recipients = []
    for recipient, donors in BLOOD_COMPATIBILITY.items():
        if donor_blood_group in donors:
            recipients.append(recipient)
    return recipients


def check_eligibility(last_donation_date):
    """Check if a donor is eligible based on last donation date (56-day rule)."""
    from datetime import date
    if not last_donation_date:
        return True, 0
    days_since = (date.today() - last_donation_date).days
    return days_since >= 56, days_since


def days_until_eligible(last_donation_date):
    """Return number of days until the donor becomes eligible again."""
    from datetime import date
    if not last_donation_date:
        return 0
    days_since = (date.today() - last_donation_date).days
    remaining = 56 - days_since
    return max(0, remaining)
