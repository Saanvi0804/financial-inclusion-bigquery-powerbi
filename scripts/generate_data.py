"""
Synthetic Data Generation Module for Financial Inclusion Analytics Warehouse.

Generates:
1. Loan Portfolio (>= 50,000 loans, specifically 52,000 loans)
2. Borrower Information (>= 45,000 borrowers, specifically 46,000 borrowers)
3. Branch Information (36 branches across 10 Indian states)
4. Repayment Transactions (>= 530,000 records)
5. Monthly Instalment Schedule (consistent reducing-balance amortization model)

Seeds 10 documented data quality anomalies for downstream detection and testing.
Uses deterministic random seed (42) to preserve verified empirical baseline.
"""

import os
import sys
import logging
from datetime import datetime, date, timedelta
import numpy as np
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("DataGenerator")

RANDOM_SEED = 42
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "raw")

# Financial & Portfolio Configuration
STATES = [
    {"state_id": "ST_MH", "state_name": "Maharashtra", "region": "West"},
    {"state_id": "ST_TN", "state_name": "Tamil Nadu", "region": "South"},
    {"state_id": "ST_UP", "state_name": "Uttar Pradesh", "region": "North"},
    {"state_id": "ST_KA", "state_name": "Karnataka", "region": "South"},
    {"state_id": "ST_BR", "state_name": "Bihar", "region": "East"},
    {"state_id": "ST_OD", "state_name": "Odisha", "region": "East"},
    {"state_id": "ST_RJ", "state_name": "Rajasthan", "region": "North"},
    {"state_id": "ST_MP", "state_name": "Madhya Pradesh", "region": "Central"},
    {"state_id": "ST_WB", "state_name": "West Bengal", "region": "East"},
    {"state_id": "ST_GJ", "state_name": "Gujarat", "region": "West"},
]

BRANCHES_DEF = [
    # Maharashtra
    ("BR001", "Pune Central", "ST_MH", "Urban"),
    ("BR002", "Nagpur East", "ST_MH", "Semi-Urban"),
    ("BR003", "Solapur Rural", "ST_MH", "Rural"),
    ("BR004", "Nashik Hub", "ST_MH", "Semi-Urban"),
    # Tamil Nadu
    ("BR005", "Chennai Metro", "ST_TN", "Urban"),
    ("BR006", "Madurai South", "ST_TN", "Semi-Urban"),
    ("BR007", "Thanjavur Rural", "ST_TN", "Rural"),
    ("BR008", "Coimbatore Hub", "ST_TN", "Urban"),
    # Uttar Pradesh
    ("BR009", "Lucknow City", "ST_UP", "Urban"),
    ("BR010", "Varanasi North", "ST_UP", "Semi-Urban"),
    ("BR011", "Gorakhpur Rural", "ST_UP", "Rural"),
    ("BR012", "Agra West", "ST_UP", "Semi-Urban"),
    # Karnataka
    ("BR013", "Bengaluru South", "ST_KA", "Urban"),
    ("BR014", "Mysuru Central", "ST_KA", "Semi-Urban"),
    ("BR015", "Belagavi Rural", "ST_KA", "Rural"),
    ("BR016", "Hubballi Hub", "ST_KA", "Semi-Urban"),
    # Bihar
    ("BR017", "Patna Hub", "ST_BR", "Urban"),
    ("BR018", "Gaya City", "ST_BR", "Semi-Urban"),
    ("BR019", "Muzaffarpur Rural", "ST_BR", "Rural"),
    ("BR020", "Bhagalpur South", "ST_BR", "Rural"),
    # Odisha
    ("BR021", "Bhubaneswar Central", "ST_OD", "Urban"),
    ("BR022", "Cuttack Metro", "ST_OD", "Semi-Urban"),
    ("BR023", "Sambalpur Rural", "ST_OD", "Rural"),
    ("BR024", "Ganjam Rural", "ST_OD", "Rural"),
    # Rajasthan
    ("BR025", "Jaipur Metro", "ST_RJ", "Urban"),
    ("BR026", "Jodhpur West", "ST_RJ", "Semi-Urban"),
    ("BR027", "Udaipur Rural", "ST_RJ", "Rural"),
    ("BR028", "Kota South", "ST_RJ", "Semi-Urban"),
    # Madhya Pradesh
    ("BR029", "Bhopal Central", "ST_MP", "Urban"),
    ("BR030", "Indore City", "ST_MP", "Urban"),
    ("BR031", "Jabalpur Rural", "ST_MP", "Rural"),
    ("BR032", "Ujjain Semi-Urban", "ST_MP", "Semi-Urban"),
    # West Bengal
    ("BR033", "Kolkata North", "ST_WB", "Urban"),
    ("BR034", "Howrah Central", "ST_WB", "Semi-Urban"),
    ("BR035", "Siliguri Rural", "ST_WB", "Rural"),
    # Gujarat
    ("BR036", "Ahmedabad Metro", "ST_GJ", "Urban"),
]

PRODUCTS_DEF = [
    {
        "product_id": "PRD_MFI",
        "product_name": "Joint Liability Group Microfinance Loan",
        "category": "Microfinance",
        "min_rate": 18.0,
        "max_rate": 24.0,
        "min_tenure": 12,
        "max_tenure": 24,
        "min_principal": 15000,
        "max_principal": 50000,
        "weight": 0.40,
        "default_risk": 0.025,
    },
    {
        "product_id": "PRD_AGR",
        "product_name": "Kisan Agri Crop & Dairy Loan",
        "category": "Agriculture",
        "min_rate": 12.0,
        "max_rate": 16.0,
        "min_tenure": 12,
        "max_tenure": 18,
        "min_principal": 30000,
        "max_principal": 120000,
        "weight": 0.22,
        "default_risk": 0.045,
    },
    {
        "product_id": "PRD_SMB",
        "product_name": "MSME Small Enterprise Working Capital",
        "category": "MSME",
        "min_rate": 16.0,
        "max_rate": 22.0,
        "min_tenure": 18,
        "max_tenure": 36,
        "min_principal": 50000,
        "max_principal": 300000,
        "weight": 0.18,
        "default_risk": 0.040,
    },
    {
        "product_id": "PRD_PER",
        "product_name": "Emergency & Consumption Personal Loan",
        "category": "Personal",
        "min_rate": 20.0,
        "max_rate": 26.0,
        "min_tenure": 12,
        "max_tenure": 24,
        "min_principal": 20000,
        "max_principal": 80000,
        "weight": 0.12,
        "default_risk": 0.070,
    },
    {
        "product_id": "PRD_EDU",
        "product_name": "Vocational Skill & Higher Education Loan",
        "category": "Education",
        "min_rate": 11.0,
        "max_rate": 15.0,
        "min_tenure": 18,
        "max_tenure": 36,
        "min_principal": 40000,
        "max_principal": 200000,
        "weight": 0.08,
        "default_risk": 0.030,
    },
]

BORROWER_SEGMENTS = [
    "Women Self-Help Group",
    "Smallholder Farmer",
    "Micro-entrepreneur",
    "Salaried Low Income",
    "Informal Sector Worker",
]

INCOME_BANDS = ["<1.5L", "1.5L-3L", "3L-5L", ">5L"]
LOCATION_TYPES = ["Rural", "Semi-Urban", "Urban"]
OCCUPATION_CATEGORIES = [
    "Agriculture & Dairy",
    "Retail & Petty Trade",
    "Artisan & Small Manufacturing",
    "Services & Transport",
    "Salaried Employment",
]

def calculate_monthly_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """Standard reducing balance EMI calculation formula."""
    r = (annual_rate / 100.0) / 12.0
    if r == 0:
        return round(principal / tenure_months, 2)
    emi = principal * (r * ((1 + r) ** tenure_months)) / (((1 + r) ** tenure_months) - 1)
    return round(float(emi), 2)

def generate_synthetic_data(num_loans: int = 52000, num_borrowers: int = 46000):
    logger.info("Initializing synthetic data generator with seed %d...", RANDOM_SEED)
    np.random.seed(RANDOM_SEED)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Branch Data
    logger.info("Generating %d branches across %d states...", len(BRANCHES_DEF), len(STATES))
    branches_df = pd.DataFrame(
        BRANCHES_DEF,
        columns=["branch_id", "branch_name", "state_id", "location_type"]
    )

    # 2. Borrower Information
    logger.info("Generating %d unique borrowers...", num_borrowers)
    borrower_ids = [f"BW{i:06d}" for i in range(1, num_borrowers + 1)]
    borrower_segments = np.random.choice(
        BORROWER_SEGMENTS, size=num_borrowers, p=[0.42, 0.22, 0.18, 0.10, 0.08]
    )
    income_bands = np.random.choice(
        INCOME_BANDS, size=num_borrowers, p=[0.35, 0.45, 0.15, 0.05]
    )
    loc_types = np.random.choice(
        LOCATION_TYPES, size=num_borrowers, p=[0.45, 0.35, 0.20]
    )
    occupations = np.random.choice(
        OCCUPATION_CATEGORIES, size=num_borrowers, p=[0.32, 0.28, 0.16, 0.14, 0.10]
    )

    borrowers_df = pd.DataFrame({
        "borrower_id": borrower_ids,
        "borrower_segment": borrower_segments,
        "income_band": income_bands,
        "location_type": loc_types,
        "occupation_category": occupations,
    })

    # 3. Loan Portfolio
    logger.info("Generating %d loans spanning 24+ months...", num_loans)
    loan_ids = [f"LN{i:06d}" for i in range(1, num_loans + 1)]
    assigned_borrowers = np.random.choice(borrower_ids, size=num_loans, replace=True)
    
    # Assign branch & state
    branch_indices = np.random.choice(len(BRANCHES_DEF), size=num_loans)
    assigned_branch_ids = [BRANCHES_DEF[idx][0] for idx in branch_indices]
    assigned_state_ids = [BRANCHES_DEF[idx][2] for idx in branch_indices]

    # Assign product
    prod_weights = [p["weight"] for p in PRODUCTS_DEF]
    prod_indices = np.random.choice(len(PRODUCTS_DEF), size=num_loans, p=prod_weights)
    assigned_product_ids = [PRODUCTS_DEF[idx]["product_id"] for idx in prod_indices]

    # Generate dates across 24 months: 2023-01-01 to 2024-12-31 (730 days)
    start_date = date(2023, 1, 1)
    day_offsets = np.random.randint(0, 730, size=num_loans)
    disbursement_dates = [start_date + timedelta(days=int(d)) for d in day_offsets]

    # Principal, Rate, Tenure
    principals = []
    interest_rates = []
    tenures = []
    for idx in prod_indices:
        p_cfg = PRODUCTS_DEF[idx]
        principal = round(float(np.random.uniform(p_cfg["min_principal"], p_cfg["max_principal"])), -2)
        rate = round(float(np.random.uniform(p_cfg["min_rate"], p_cfg["max_rate"])), 2)
        if p_cfg["min_tenure"] == p_cfg["max_tenure"]:
            tenure = p_cfg["min_tenure"]
        else:
            tenure = int(np.random.choice([p_cfg["min_tenure"], (p_cfg["min_tenure"] + p_cfg["max_tenure"]) // 2, p_cfg["max_tenure"]]))
        principals.append(principal)
        interest_rates.append(rate)
        tenures.append(tenure)

    loans_df = pd.DataFrame({
        "loan_id": loan_ids,
        "borrower_id": assigned_borrowers,
        "branch_id": assigned_branch_ids,
        "state_id": assigned_state_ids,
        "product_id": assigned_product_ids,
        "disbursement_date": disbursement_dates,
        "principal_amount": principals,
        "annual_interest_rate": interest_rates,
        "tenure_months": tenures,
        "loan_status": "Active" # Will be updated after instalment simulation
    })

    # 4. Monthly Instalment Schedule and Repayments
    logger.info("Simulating monthly instalments and repayments with financial consistency...")
    
    simulation_end_date = date(2024, 12, 31)

    instalment_rows = []
    repayment_rows = []
    loan_status_list = []
    
    tx_counter = 1
    inst_counter = 1

    for row in loans_df.itertuples():
        l_id = row.loan_id
        p_id = row.product_id
        b_id = row.branch_id
        p_amt = row.principal_amount
        r_rate = row.annual_interest_rate
        tenure = row.tenure_months
        d_date = row.disbursement_date

        emi = calculate_monthly_emi(p_amt, r_rate, tenure)
        
        base_risk = next(p["default_risk"] for p in PRODUCTS_DEF if p["product_id"] == p_id)
        branch_mod = 1.6 if b_id == "BR025" else (0.6 if b_id == "BR005" else 1.0)
        loan_risk = base_risk * branch_mod

        profile_rand = np.random.rand()
        if profile_rand < (loan_risk * 0.7):
            profile = 2 # Defaulter
        elif profile_rand < (loan_risk * 2.2):
            profile = 1 # Late payer
        else:
            profile = 0 # Good payer

        current_opening = float(p_amt)
        monthly_r = (r_rate / 100.0) / 12.0
        total_missed = 0
        total_paid_count = 0

        for inst_num in range(1, tenure + 1):
            m = d_date.month + inst_num
            y = d_date.year + (m - 1) // 12
            m = (m - 1) % 12 + 1
            day = min(d_date.day, 28)
            due_date = date(y, m, day)

            interest_comp = round(current_opening * monthly_r, 2)
            if inst_num == tenure:
                principal_comp = round(current_opening, 2)
                amt_due = round(principal_comp + interest_comp, 2)
                closing_prin = 0.00
            else:
                principal_comp = round(emi - interest_comp, 2)
                amt_due = emi
                closing_prin = round(current_opening - principal_comp, 2)

            if due_date > simulation_end_date:
                amt_paid = 0.0
                dpd = 0
                out_inst = amt_due
            else:
                if profile == 0:
                    amt_paid = amt_due
                    dpd = 0
                    out_inst = 0.0
                    pay_date = due_date - timedelta(days=int(np.random.choice([0, 1, 2])))
                elif profile == 1:
                    is_partial = (np.random.rand() < 0.20)
                    if is_partial:
                        amt_paid = round(amt_due * float(np.random.choice([0.4, 0.5, 0.6])), 2)
                        dpd = int(np.random.randint(31, 60))
                        out_inst = round(amt_due - amt_paid, 2)
                        pay_date = due_date + timedelta(days=int(np.random.randint(10, 30)))
                    else:
                        amt_paid = amt_due
                        dpd = int(np.random.randint(15, 45))
                        out_inst = 0.0
                        pay_date = due_date + timedelta(days=dpd)
                else: # Profile 2: Defaulter
                    if inst_num <= 2:
                        amt_paid = amt_due
                        dpd = 0
                        out_inst = 0.0
                        pay_date = due_date
                    else:
                        amt_paid = 0.0
                        dpd = min(365, (simulation_end_date - due_date).days)
                        out_inst = amt_due
                        pay_date = None
                        total_missed += 1

                if amt_paid > 0 and pay_date is not None:
                    days_from_start = max(0, min(730, (pay_date - start_date).days))
                    progress_ratio = days_from_start / 730.0
                    p_upi = 0.20 + (0.40 * progress_ratio)
                    p_bank = 0.15 + (0.07 * progress_ratio)
                    p_cash = max(0.05, 1.0 - p_upi - p_bank)
                    p_channel = np.random.choice(["UPI", "Bank Transfer", "Cash"], p=[p_upi, p_bank, p_cash])

                    repayment_rows.append((
                        f"TXN{tx_counter:08d}",
                        l_id,
                        pay_date,
                        amt_paid,
                        p_channel,
                        "INR"
                    ))
                    tx_counter += 1
                    total_paid_count += 1

            inst_id = f"INS{inst_counter:08d}"
            instalment_rows.append((
                inst_id,
                l_id,
                due_date,
                inst_num,
                current_opening,
                amt_due,
                principal_comp,
                interest_comp,
                closing_prin,
                amt_paid,
                dpd,
                out_inst
            ))
            inst_counter += 1
            current_opening = closing_prin

        maturity_date = date(
            d_date.year + (d_date.month + tenure - 1) // 12,
            (d_date.month + tenure - 1) % 12 + 1,
            min(d_date.day, 28)
        )
        if maturity_date <= simulation_end_date and total_missed == 0:
            status = "Closed"
        elif total_missed >= 3 or profile == 2:
            status = "Defaulted"
        else:
            status = "Active"
        loan_status_list.append(status)

    loans_df["loan_status"] = loan_status_list

    instalments_df = pd.DataFrame(
        instalment_rows,
        columns=[
            "instalment_id", "loan_id", "due_date", "instalment_number",
            "opening_principal", "amount_due", "principal_component", "interest_component",
            "closing_principal", "amount_paid", "days_past_due", "outstanding_instalment_amount"
        ]
    )

    repayments_df = pd.DataFrame(
        repayment_rows,
        columns=["transaction_id", "loan_id", "payment_date", "payment_amount", "payment_channel", "amount_unit"]
    )

    logger.info("Base counts generated:")
    logger.info("  Loans: %d", len(loans_df))
    logger.info("  Borrowers: %d", len(borrowers_df))
    logger.info("  Branches: %d", len(branches_df))
    logger.info("  Instalments: %d", len(instalments_df))
    logger.info("  Repayments: %d", len(repayments_df))

    # =========================================================================
    # INTENTIONAL SEEDING OF 10 DATA QUALITY ANOMALIES
    # =========================================================================
    logger.info("Seeding 10 documented data quality anomalies...")

    # Issue 1: Duplicate loan records (200 records)
    dup_loans = loans_df.iloc[:200].copy()
    loans_df = pd.concat([loans_df, dup_loans], ignore_index=True)
    logger.info("  [Issue 1] Seeded 200 duplicate loan records.")

    # Issue 2: Duplicate payment transactions (400 records)
    dup_repayments = repayments_df.iloc[:400].copy()
    repayments_df = pd.concat([repayments_df, dup_repayments], ignore_index=True)
    logger.info("  [Issue 2] Seeded 400 duplicate payment transactions.")

    # Issue 3: Missing monthly data for one branch (Branch BR025 in Oct 2024)
    br25_loans = set(loans_df[loans_df["branch_id"] == "BR025"]["loan_id"])
    oct_start = date(2024, 10, 1)
    oct_end = date(2024, 10, 31)
    
    before_tx = len(repayments_df)
    repayments_df = repayments_df[
        ~((repayments_df["loan_id"].isin(br25_loans)) &
          (repayments_df["payment_date"] >= oct_start) &
          (repayments_df["payment_date"] <= oct_end))
    ]
    logger.info("  [Issue 3] Omitted Oct 2024 branch BR025 repayment records (%d txns removed).", before_tx - len(repayments_df))

    # Issue 4: Amounts stored in different units (500 records stored in paise = 100x INR, explicit amount_unit='PAISE')
    paise_indices = np.random.choice(len(repayments_df), size=500, replace=False)
    repayments_df.iloc[paise_indices, repayments_df.columns.get_loc("payment_amount")] = (
        repayments_df.iloc[paise_indices]["payment_amount"] * 100.0
    )
    repayments_df.iloc[paise_indices, repayments_df.columns.get_loc("amount_unit")] = "PAISE"
    logger.info("  [Issue 4] Seeded 500 transactions with amounts in paise (100x) and amount_unit='PAISE'.")

    # Issue 5: Negative transaction amounts (150 records)
    neg_indices = np.random.choice([i for i in range(len(repayments_df)) if i not in paise_indices], size=150, replace=False)
    repayments_df.iloc[neg_indices, repayments_df.columns.get_loc("payment_amount")] = (
        -1.0 * np.abs(repayments_df.iloc[neg_indices]["payment_amount"])
    )
    logger.info("  [Issue 5] Seeded 150 negative payment amounts.")

    # Issue 6: Missing branch identifiers (250 loans)
    missing_branch_idx = np.random.choice(len(loans_df), size=250, replace=False)
    loans_df.iloc[missing_branch_idx, loans_df.columns.get_loc("branch_id")] = ""
    logger.info("  [Issue 6] Seeded 250 loans with missing/blank branch_id.")

    # Issue 7: Invalid loan product identifiers (180 loans)
    invalid_prod_idx = np.random.choice([i for i in range(len(loans_df)) if i not in missing_branch_idx], size=180, replace=False)
    loans_df.iloc[invalid_prod_idx, loans_df.columns.get_loc("product_id")] = "PRD_INVALID"
    logger.info("  [Issue 7] Seeded 180 loans with invalid product_id 'PRD_INVALID'.")

    # Issue 8: Instalment payments exceeding scheduled amounts (220 instalments)
    excess_inst_idx = np.random.choice(len(instalments_df), size=220, replace=False)
    instalments_df.iloc[excess_inst_idx, instalments_df.columns.get_loc("amount_paid")] = (
        instalments_df.iloc[excess_inst_idx]["amount_due"] * 2.8
    )
    logger.info("  [Issue 8] Seeded 220 instalment records with payment exceeding 2.8x schedule.")

    # Issue 9: Payment dates before loan disbursement (160 transactions)
    early_tx_idx = np.random.choice(len(repayments_df), size=160, replace=False)
    loan_disb_map = dict(zip(loans_df["loan_id"], loans_df["disbursement_date"]))
    new_dates = []
    for idx in early_tx_idx:
        l_id = repayments_df.iloc[idx]["loan_id"]
        d_dt = loan_disb_map.get(l_id, date(2023, 6, 1))
        new_dates.append(d_dt - timedelta(days=int(np.random.randint(5, 30))))
    repayments_df.iloc[early_tx_idx, repayments_df.columns.get_loc("payment_date")] = new_dates
    logger.info("  [Issue 9] Seeded 160 transactions where payment_date < disbursement_date.")

    # Issue 10: Incorrect days-past-due values (350 instalments)
    overdue_candidates = instalments_df[instalments_df["days_past_due"] > 30].index
    if len(overdue_candidates) >= 350:
        bad_dpd_idx = np.random.choice(overdue_candidates, size=350, replace=False)
    else:
        bad_dpd_idx = np.random.choice(len(instalments_df), size=350, replace=False)
    instalments_df.iloc[bad_dpd_idx, instalments_df.columns.get_loc("days_past_due")] = 0
    logger.info("  [Issue 10] Seeded 350 instalments with corrupted 0 DPD despite arrears.")

    # =========================================================================
    # PERSIST RAW CSV FILES
    # =========================================================================
    logger.info("Persisting immutable raw datasets to %s...", OUTPUT_DIR)
    loans_df.to_csv(os.path.join(OUTPUT_DIR, "loans.csv"), index=False)
    borrowers_df.to_csv(os.path.join(OUTPUT_DIR, "borrowers.csv"), index=False)
    branches_df.to_csv(os.path.join(OUTPUT_DIR, "branches.csv"), index=False)
    repayments_df.to_csv(os.path.join(OUTPUT_DIR, "repayments.csv"), index=False)
    instalments_df.to_csv(os.path.join(OUTPUT_DIR, "instalments.csv"), index=False)

    logger.info("Raw synthetic data generation successfully completed!")
    logger.info("Final raw file records:")
    logger.info("  loans.csv: %d rows", len(loans_df))
    logger.info("  borrowers.csv: %d rows", len(borrowers_df))
    logger.info("  branches.csv: %d rows", len(branches_df))
    logger.info("  repayments.csv: %d rows", len(repayments_df))
    logger.info("  instalments.csv: %d rows", len(instalments_df))

if __name__ == "__main__":
    generate_synthetic_data()
