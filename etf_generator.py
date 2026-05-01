#!/usr/bin/env python3
"""
ETF MEMTXT File Generator
--------------------------
Generates the MEMTXT.TXT file required for Sri Lanka ETF (Employee Trust Fund)
monthly contributions, ready for upload to the bank portal.

Usage:
    python3 etf_generator.py

Requirements:
    No external libraries needed — uses Python standard library only.

Author: Generated for your Sri Lanka startup (3 employees)
"""

import os
import json
from datetime import datetime, date
from pathlib import Path


# ─────────────────────────────────────────────
#  CONFIG FILE  (saved so you don't re-type every month)
# ─────────────────────────────────────────────

CONFIG_FILE = Path(__file__).parent / "etf_config.json"


def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    print(f"  ✓ Config saved to {CONFIG_FILE}")


# ─────────────────────────────────────────────
#  FORMAT HELPERS  (match the spec exactly)
# ─────────────────────────────────────────────

def fmt_employer_number(emp_no: str) -> str:
    """
    Employer number must be AANNNNNN (2 alpha + 6 digits), total 8 chars.
    Accepts formats like 'A/3057', 'A 3057', 'AB123456', 'DB022222', etc.
    """
    # Strip slashes/spaces and normalise
    clean = emp_no.replace("/", "").replace(" ", "").strip().upper()
    if len(clean) < 2:
        raise ValueError(f"Employer number too short: '{emp_no}'")
    alpha_part = ""
    digit_part = ""
    for ch in clean:
        if ch.isalpha() and not digit_part:
            alpha_part += ch
        elif ch.isdigit():
            digit_part += ch
        else:
            raise ValueError(f"Unexpected character '{ch}' in employer number '{emp_no}'")
    # Pad to 2 alpha + 6 digits
    alpha_part = alpha_part.ljust(2)[:2]
    digit_part = digit_part.zfill(6)[:6]
    return alpha_part + digit_part  # exactly 8 chars


def fmt_period(year: int, month: int) -> str:
    """YYYYMM format (6 chars)"""
    return f"{year:04d}{month:02d}"


def fmt_name_initials(initials: str) -> str:
    """
    Initials: left-aligned, upper case, no dots/commas, separated by single space.
    Field is 20 chars.
    """
    parts = initials.replace(".", "").replace(",", "").upper().split()
    result = " ".join(parts)
    return result.ljust(20)[:20]


def fmt_surname(surname: str) -> str:
    """Surname: left-aligned, upper case, 30 chars."""
    clean = surname.replace(".", "").replace(",", "").upper().strip()
    return clean.ljust(30)[:30]


def fmt_nic(nic: str) -> str:
    """NIC: left-aligned, 12 chars."""
    return nic.strip().upper().ljust(12)[:12]


def fmt_member_number(mem_no: int) -> str:
    """Member number: 6 digits, right-aligned, zero-padded."""
    return str(mem_no).zfill(6)[:6]


def fmt_amount_cents(amount_lkr: float) -> str:
    """
    Convert LKR amount to cents and right-align in 9-char field.
    e.g. Rs. 1800.00 → 180000 (in cents) → '000180000'
    """
    cents = round(amount_lkr * 100)
    return str(cents).zfill(9)[:9]


def fmt_total_cents_header(amount_lkr: float) -> str:
    """Header total: 14-char field in cents."""
    cents = round(amount_lkr * 100)
    return str(cents).zfill(14)[:14]


def fmt_total_members(count: int) -> str:
    """6-char zero-padded member count."""
    return str(count).zfill(6)[:6]


# ─────────────────────────────────────────────
#  RECORD BUILDERS
# ─────────────────────────────────────────────

def build_detail_record(employer_no: str, member_seq: int, initials: str,
                        surname: str, nic: str, period_year: int,
                        period_month: int, contribution_lkr: float) -> str:
    """
    Detail record — 98 chars long.

    Pos  1      : 'D'
    Pos  2-9    : Employer number (8)
    Pos 10-15   : Member number (6)
    Pos 16-35   : Initials (20)
    Pos 36-65   : Surname (30)
    Pos 66-77   : NIC (12)
    Pos 78-83   : Period from (6)
    Pos 84-89   : Period to (6)
    Pos 90-98   : Contribution in cents (9)
    """
    period = fmt_period(period_year, period_month)
    record = (
        "D"
        + fmt_employer_number(employer_no)      #  2-9
        + fmt_member_number(member_seq)          # 10-15
        + fmt_name_initials(initials)            # 16-35
        + fmt_surname(surname)                   # 36-65
        + fmt_nic(nic)                           # 66-77
        + period                                 # 78-83
        + period                                 # 84-89  (same month, from=to)
        + fmt_amount_cents(contribution_lkr)     # 90-98
    )
    assert len(record) == 98, f"Detail record length {len(record)} != 98"
    return record


def build_header_record(employer_no: str, period_year: int, period_month: int,
                        total_members: int, total_lkr: float) -> str:
    """
    Header record — 43 chars long (spec ends at pos 43).

    Pos  1    : 'H'
    Pos  2-9  : Employer number (8)
    Pos 10-15 : Period from (6)
    Pos 16-21 : Period to (6)
    Pos 22-27 : Total members (6)
    Pos 28-41 : Total contribution in cents (14)
    Pos 42-43 : Lines per page — fixed '24' (2)
    """
    period = fmt_period(period_year, period_month)
    record = (
        "H"
        + fmt_employer_number(employer_no)      #  2-9
        + period                                # 10-15
        + period                                # 16-21
        + fmt_total_members(total_members)      # 22-27
        + fmt_total_cents_header(total_lkr)     # 28-41
        + "24"                                  # 42-43
    )
    assert len(record) == 43, f"Header record length {len(record)} != 43"
    return record


# ─────────────────────────────────────────────
#  INTERACTIVE INPUT HELPERS
# ─────────────────────────────────────────────

def ask(prompt: str, default: str = "") -> str:
    if default:
        val = input(f"  {prompt} [{default}]: ").strip()
        return val if val else default
    else:
        while True:
            val = input(f"  {prompt}: ").strip()
            if val:
                return val
            print("    ⚠  This field is required.")


def ask_float(prompt: str, default: float = None) -> float:
    default_str = f"{default:.2f}" if default is not None else ""
    while True:
        raw = ask(prompt, default_str)
        try:
            return float(raw)
        except ValueError:
            print("    ⚠  Please enter a valid number (e.g. 1800 or 1800.50).")


def ask_int(prompt: str, default: int = None) -> int:
    default_str = str(default) if default is not None else ""
    while True:
        raw = ask(prompt, default_str)
        try:
            return int(raw)
        except ValueError:
            print("    ⚠  Please enter a whole number.")


# ─────────────────────────────────────────────
#  MAIN PROGRAM
# ─────────────────────────────────────────────

def main():
    print()
    print("=" * 55)
    print("   ETF MEMTXT File Generator — Sri Lanka")
    print("=" * 55)
    print()

    config = load_config()

    # ── Step 1: Employer details ──────────────────────────────
    print("── EMPLOYER DETAILS ─────────────────────────────────")
    print("(These are saved so you only enter them once.)\n")

    employer_no = ask(
        "Employer ETF number (e.g. DB022222 or A/3057)",
        config.get("employer_no", "")
    )
    config["employer_no"] = employer_no

    # ── Step 2: Contribution period ───────────────────────────
    print()
    print("── CONTRIBUTION PERIOD ──────────────────────────────")
    today = date.today()
    # Default = previous month
    default_year  = today.year  if today.month > 1 else today.year - 1
    default_month = today.month - 1 if today.month > 1 else 12

    period_year  = ask_int("Year  (YYYY)", config.get("last_year",  default_year))
    period_month = ask_int("Month (1-12)", config.get("last_month", default_month))

    if not (1 <= period_month <= 12):
        print("  ⚠  Invalid month. Using previous month instead.")
        period_month = default_month

    config["last_year"]  = period_year
    config["last_month"] = period_month

    # ── Step 3: Employee details ───────────────────────────────
    print()
    print("── EMPLOYEE CONTRIBUTIONS ───────────────────────────")
    print("(Enter each employee's details. Press Enter to reuse saved values.)\n")

    saved_employees = config.get("employees", [])
    employees = []

    # Ask how many employees
    num_emp = ask_int("Number of employees", len(saved_employees) if saved_employees else 3)

    for i in range(num_emp):
        print(f"\n  Employee {i+1}:")
        saved = saved_employees[i] if i < len(saved_employees) else {}

        initials    = ask("  Initials (e.g. A B C)",         saved.get("initials", ""))
        surname     = ask("  Surname",                        saved.get("surname",  ""))
        nic         = ask("  NIC number",                     saved.get("nic",      ""))
        member_no   = ask_int("  Member sequence number",     saved.get("member_no", i + 4))
        contrib     = ask_float("  Contribution this month (LKR)", saved.get("default_contrib", 1500.0))

        employees.append({
            "initials":         initials,
            "surname":          surname,
            "nic":              nic,
            "member_no":        member_no,
            "default_contrib":  contrib,
            "contrib_this_month": contrib,
        })

    config["employees"] = [
        {k: v for k, v in e.items() if k != "contrib_this_month"}
        for e in employees
    ]

    # ── Step 4: Build records ─────────────────────────────────
    print()
    print("── GENERATING FILE ──────────────────────────────────")

    total_lkr = sum(e["contrib_this_month"] for e in employees)

    # Build detail records
    detail_lines = []
    for emp in employees:
        line = build_detail_record(
            employer_no     = employer_no,
            member_seq      = emp["member_no"],
            initials        = emp["initials"],
            surname         = emp["surname"],
            nic             = emp["nic"],
            period_year     = period_year,
            period_month    = period_month,
            contribution_lkr= emp["contrib_this_month"],
        )
        detail_lines.append(line)

    # Build header record
    header_line = build_header_record(
        employer_no   = employer_no,
        period_year   = period_year,
        period_month  = period_month,
        total_members = len(employees),
        total_lkr     = total_lkr,
    )

    # Combine: Detail records first, then Header at the end (matches sample)
    all_lines = detail_lines + [header_line]
    file_content = "\n".join(all_lines)

    # ── Step 5: Write file ────────────────────────────────────
    output_dir  = Path(__file__).parent / "etf_output"
    output_dir.mkdir(exist_ok=True)

    month_label = f"{period_year}{period_month:02d}"
    output_path = output_dir / f"MEMTXT_{month_label}.TXT"

    with open(output_path, "w", newline="\r\n") as f:
        f.write(file_content)

    # Also write the standard name the portal expects
    portal_path = output_dir / "MEMTXT.TXT"
    with open(portal_path, "w", newline="\r\n") as f:
        f.write(file_content)

    # ── Step 6: Summary ───────────────────────────────────────
    print()
    print("  ✓ File written successfully!")
    print()
    print(f"  Period     : {period_year}/{period_month:02d}")
    print(f"  Employees  : {len(employees)}")
    print(f"  Total (LKR): {total_lkr:,.2f}")
    print()
    print(f"  Files saved to: {output_dir}/")
    print(f"    • MEMTXT.TXT          ← upload this to the bank portal")
    print(f"    • MEMTXT_{month_label}.TXT  ← your monthly archive copy")
    print()
    print("  Preview of file content:")
    print("  " + "-" * 50)
    for line in all_lines:
        print(f"  {line}")
    print("  " + "-" * 50)
    print()

    # Save config for next month
    save_config(config)
    print()
    print("  All done! Your config is saved — next month will be even faster.")
    print()


if __name__ == "__main__":
    main()
