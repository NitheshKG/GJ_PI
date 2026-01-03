#!/usr/bin/env python3
"""
Test script to verify the new pending interest months calculation
with decimal support (5.5 months format)
"""
from datetime import datetime, timedelta
from calendar import monthrange

def calculate_completed_months(start_date, end_date):
    """
    Calculate the number of complete months between two dates, including fractional months.
    """
    # Calculate raw month difference
    months_diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
    
    # Track the fractional part
    fractional_months = 0.0
    
    # If we're in the same month, calculate fractional months based on days
    if start_date.year == end_date.year and start_date.month == end_date.month:
        days_elapsed = (end_date - start_date).days
        fractional_months = days_elapsed / 30.0
        return max(0, fractional_months)
    
    # If the day of end_date is less than day of start_date
    if end_date.day < start_date.day:
        months_diff -= 1
        days_in_month = monthrange(end_date.year, end_date.month)[1]
        fractional_months = end_date.day / 30.0
    else:
        # We have completed this month
        days_into_month = end_date.day - start_date.day
        fractional_months = days_into_month / 30.0
    
    # Combine complete months with fractional months
    total_months = max(0, months_diff) + fractional_months
    return round(total_months, 2)

# Test cases
print("=" * 60)
print("PENDING INTEREST MONTHS CALCULATION TESTS")
print("=" * 60)

test_cases = [
    # (start_date, end_date, description)
    (datetime(2025, 11, 8), datetime(2025, 11, 8), "Same day"),
    (datetime(2025, 11, 8), datetime(2025, 11, 15), "7 days into same month"),
    (datetime(2025, 11, 8), datetime(2025, 11, 30), "22 days into same month"),
    (datetime(2025, 11, 8), datetime(2025, 12, 5), "Before completing 1st month"),
    (datetime(2025, 11, 8), datetime(2025, 12, 8), "Exactly 1 complete month"),
    (datetime(2025, 11, 8), datetime(2025, 12, 15), "1 month + 7 days"),
    (datetime(2025, 11, 8), datetime(2026, 1, 7), "1 month + 30 days (almost 2)"),
    (datetime(2025, 11, 8), datetime(2026, 1, 8), "Exactly 2 complete months"),
    (datetime(2025, 11, 8), datetime(2026, 1, 15), "2 months + 7 days"),
    (datetime(2025, 11, 8), datetime(2026, 3, 8), "Exactly 4 complete months"),
    (datetime(2025, 11, 8), datetime(2026, 3, 20), "4 months + 12 days"),
]

for start, end, description in test_cases:
    months = calculate_completed_months(start, end)
    print(f"\n{description}")
    print(f"  Start: {start.strftime('%b %d, %Y')}")
    print(f"  End:   {end.strftime('%b %d, %Y')}")
    print(f"  Pending Months: {months}")

print("\n" + "=" * 60)
print("EXAMPLE: Payment Scenario")
print("=" * 60)
print("\nTicket Created: Nov 8, 2025")
print("Interest Rate: 2% per month")
print("Principal: ₹20,000")

dates_to_check = [
    datetime(2025, 11, 15),
    datetime(2025, 12, 8),
    datetime(2025, 12, 15),
    datetime(2026, 1, 7),
    datetime(2026, 1, 8),
    datetime(2026, 1, 15),
    datetime(2026, 2, 8),
    datetime(2026, 2, 15),
    datetime(2026, 3, 8),
]

start = datetime(2025, 11, 8)
for check_date in dates_to_check:
    pending = calculate_completed_months(start, check_date)
    print(f"\n{check_date.strftime('%b %d, %Y')}: {pending} months pending")
