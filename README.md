# 🇱🇰 Sri Lanka ETF MEMTXT Generator

A Python CLI tool that generates the `MEMTXT.TXT` file required for **Employee Trust Fund (ETF)** monthly contributions — ready to upload directly to your bank's payment portal.

Built for **Mac and Linux users** who can't run the Excel macro-based generator provided by banks like Commercial Bank of Sri Lanka.

---

## The Problem

Sri Lankan employers must submit monthly ETF (Form II) contributions via a specially formatted fixed-width text file (`MEMTXT.TXT`). Banks typically provide an **Excel file with VBA macros** to generate this — but those macros **don't work on macOS**.

This tool solves that: a simple Python script, no Excel needed, runs on any OS.

---

## Features

- ✅ Generates a spec-compliant `MEMTXT.TXT` for bank portal upload
- ✅ Saves an **archive copy** per month (e.g. `MEMTXT_202605.TXT`)
- ✅ **Remembers your settings** — employer number and employee details saved locally, so each month you just confirm and go
- ✅ No external libraries — uses Python's standard library only
- ✅ Works on **macOS, Linux, and Windows**
- ✅ Handles all formatting rules: cents conversion, zero-padding, name normalisation, fixed field widths

---

## Requirements

- Python 3.7 or later

Check your Python version:
```bash
python3 --version
```

---

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/sri-lanka-etf-generator.git
cd sri-lanka-etf-generator
```

### 2. Run the script

```bash
python3 etf_generator.py
```

### 3. Follow the prompts

The script will ask for:
- Your **Employer ETF number** (e.g. `DB022222` or `A/2222`)
- The **contribution period** (year and month)
- Each **employee's** initials, surname, NIC, and contribution amount (LKR)

### 4. Upload the file

Find your generated file in the `etf_output/` folder:

```
etf_output/
├── MEMTXT.TXT            ← upload this to your bank portal
└── MEMTXT_202605.TXT     ← your monthly archive copy
```

---

## From the Second Month Onwards

Your details are saved in `etf_config.json`. The next time you run it, everything is pre-filled — just press **Enter** to confirm each value and update any contribution amounts that changed.

---

## File Format

This tool follows the **EFT Payments — File Format for sending Form II Details** specification:

| Record | Length | Description |
|--------|--------|-------------|
| Detail (`D`) | 98 chars | One per employee |
| Header (`H`) | 43 chars | One per file (at end) |

Key formatting rules applied automatically:
- Names → UPPERCASE, no dots/commas, initials space-separated
- Amounts → converted to **cents**, right-aligned with leading zeros
- NIC → left-aligned, 12-char field
- Employer number → `AANNNNNN` format (2 alpha + 6 digits)

---

## Configuration File

After the first run, a `etf_config.json` file is created in the same folder:

```json
{
  "employer_no": "DB052030",
  "last_year": 2026,
  "last_month": 5,
  "employees": [
    {
      "initials": "A B C",
      "surname": "PERERA",
      "nic": "12345678V",
      "member_no": 4,
      "default_contrib": 1800.0
    }
  ]
}
```


## Disclaimer

- Always **verify the generated file** against your bank's current format requirements before submitting.
- ETF regulations and file format specifications may change. Check with your bank if submissions are rejected.
- This tool is provided as-is, without warranty. The author is not responsible for incorrect submissions.
- This is **not** official software from the ETF Board or any bank.

---

## Contributing

Pull requests are welcome! If your bank uses a slightly different format variant, feel free to open an issue or PR.

---

## Acknowledgements

Built with assistance from **Claude** by [Anthropic](https://anthropic.com).

---

## Licence

[MIT](LICENSE)
