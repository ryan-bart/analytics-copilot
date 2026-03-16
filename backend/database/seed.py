"""Seed the insurance database with realistic sample data."""

import os
import random
from datetime import date, datetime, timedelta

from faker import Faker
from sqlalchemy import inspect

from backend.database.engine import SessionLocal, engine
from backend.database.models import Base, Claim, Customer, Payment, Policy

fake = Faker()
Faker.seed(42)
random.seed(42)

PRODUCT_LINES = ["Auto", "Home", "Life", "Commercial", "Health"]
PRODUCT_WEIGHTS = [0.35, 0.25, 0.15, 0.15, 0.10]

POLICY_STATUSES = ["Active", "Cancelled", "Expired"]
POLICY_STATUS_WEIGHTS = [0.65, 0.15, 0.20]

REGIONS = ["Northeast", "Southeast", "Midwest", "West", "Southwest"]
REGION_STATES = {
    "Northeast": ["CT", "ME", "MA", "NH", "NJ", "NY", "PA", "RI", "VT"],
    "Southeast": ["AL", "FL", "GA", "KY", "MS", "NC", "SC", "TN", "VA"],
    "Midwest": ["IL", "IN", "IA", "MI", "MN", "MO", "OH", "WI"],
    "West": ["AZ", "CA", "CO", "NV", "OR", "UT", "WA"],
    "Southwest": ["AR", "LA", "NM", "OK", "TX"],
}

CLAIM_TYPES = ["Collision", "Liability", "Comprehensive", "Property Damage", "Medical"]
CLAIM_STATUSES = ["Open", "Closed", "Under Review", "Denied"]
CLAIM_STATUS_WEIGHTS = [0.15, 0.50, 0.20, 0.15]

PAYMENT_METHODS = ["Credit Card", "ACH", "Check", "Wire Transfer"]
PAYMENT_STATUSES = ["Completed", "Pending", "Failed"]
PAYMENT_STATUS_WEIGHTS = [0.85, 0.10, 0.05]

PREMIUM_RANGES = {
    "Auto": (800, 3000),
    "Home": (1200, 5000),
    "Life": (500, 2500),
    "Commercial": (3000, 15000),
    "Health": (2000, 8000),
}


def _random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def seed_database() -> dict[str, int]:
    """Seed the database and return counts of created records."""
    os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(engine)

    # Skip if already seeded
    if inspect(engine).has_table("customers"):
        with SessionLocal() as session:
            if session.query(Customer).count() > 0:
                counts = {
                    "customers": session.query(Customer).count(),
                    "policies": session.query(Policy).count(),
                    "claims": session.query(Claim).count(),
                    "payments": session.query(Payment).count(),
                }
                print(f"Database already seeded: {counts}")
                return counts

    with SessionLocal() as session:
        # Create customers
        customers = []
        for _ in range(200):
            region = random.choice(REGIONS)
            state = random.choice(REGION_STATES[region])
            customer = Customer(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.unique.email(),
                phone=fake.phone_number()[:20],
                state=state,
                region=region,
                created_at=fake.date_time_between(
                    start_date=datetime(2021, 1, 1),
                    end_date=datetime(2024, 12, 31),
                ),
            )
            customers.append(customer)
        session.add_all(customers)
        session.flush()

        # Create policies
        policies = []
        policy_counter = 0
        for customer in customers:
            num_policies = random.choices([1, 2, 3, 4], weights=[0.4, 0.35, 0.2, 0.05])[0]
            for _ in range(num_policies):
                product_line = random.choices(PRODUCT_LINES, weights=PRODUCT_WEIGHTS)[0]
                status = random.choices(POLICY_STATUSES, weights=POLICY_STATUS_WEIGHTS)[0]
                premium_min, premium_max = PREMIUM_RANGES[product_line]
                premium = round(random.uniform(premium_min, premium_max), 2)
                start = _random_date(date(2022, 1, 1), date(2025, 6, 1))
                end = start + timedelta(days=random.choice([365, 180, 730]))
                policy_counter += 1

                policy = Policy(
                    customer_id=customer.id,
                    policy_number=f"POL-{policy_counter:06d}",
                    product_line=product_line,
                    status=status,
                    premium=premium,
                    deductible=round(random.choice([250, 500, 1000, 2000, 2500]), 2),
                    coverage_limit=round(
                        random.choice([50000, 100000, 250000, 500000, 1000000]), 2
                    ),
                    start_date=start,
                    end_date=end,
                    region=customer.region,
                )
                policies.append(policy)
        session.add_all(policies)
        session.flush()

        # Create claims (~60% of policies have 0-2 claims)
        claims = []
        claim_counter = 0
        for policy in policies:
            if random.random() > 0.6:
                continue
            num_claims = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
            for _ in range(num_claims):
                claim_counter += 1
                filed = _random_date(policy.start_date, min(policy.end_date, date(2025, 12, 31)))
                status = random.choices(CLAIM_STATUSES, weights=CLAIM_STATUS_WEIGHTS)[0]
                amount_claimed = round(random.uniform(500, min(policy.coverage_limit, 50000)), 2)
                amount_paid = (
                    round(amount_claimed * random.uniform(0.3, 1.0), 2)
                    if status == "Closed"
                    else 0.0
                )
                resolved = (
                    filed + timedelta(days=random.randint(7, 120))
                    if status in ("Closed", "Denied")
                    else None
                )

                claim = Claim(
                    policy_id=policy.id,
                    claim_number=f"CLM-{claim_counter:06d}",
                    claim_type=random.choice(CLAIM_TYPES),
                    status=status,
                    amount_claimed=amount_claimed,
                    amount_paid=amount_paid,
                    filed_date=filed,
                    resolved_date=resolved,
                    description=fake.sentence(nb_words=8),
                )
                claims.append(claim)
        session.add_all(claims)
        session.flush()

        # Create payments (~2 per policy on average)
        payments = []
        for policy in policies:
            num_payments = random.choices([1, 2, 3, 4], weights=[0.2, 0.4, 0.3, 0.1])[0]
            monthly_amount = round(policy.premium / 12, 2)
            for i in range(num_payments):
                payment_date = policy.start_date + timedelta(days=30 * (i + 1))
                if payment_date > date(2025, 12, 31):
                    break
                payment = Payment(
                    policy_id=policy.id,
                    amount=monthly_amount,
                    payment_date=payment_date,
                    payment_method=random.choice(PAYMENT_METHODS),
                    status=random.choices(PAYMENT_STATUSES, weights=PAYMENT_STATUS_WEIGHTS)[0],
                )
                payments.append(payment)
        session.add_all(payments)
        session.commit()

        counts = {
            "customers": len(customers),
            "policies": len(policies),
            "claims": len(claims),
            "payments": len(payments),
        }
        print(f"Database seeded: {counts}")
        return counts


if __name__ == "__main__":
    seed_database()
