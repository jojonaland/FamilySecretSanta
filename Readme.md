# 🎁 Family Secret Santa Organizer

A Python script that organizes a balanced and fair **Secret Santa gift exchange** within a large family.  
It automatically assigns who gives gifts to whom while respecting family relationships (no gifts between parents/children, grandparents/grandchildren, etc.).

## ✨ Features
- Prevents direct gift exchanges within close family (parent–child, grandparent–grandchild, cousins).
- Encourages variety: each giver offers ideally **1 gift to an adult and 1 to a child**.
- Uses a **custom scoring system** with penalties and bonuses.
- Exports results to an **Excel file** with two sheets:
  - `Gives To`: shows who gives gifts to whom.
  - `Receives From`: shows who receives from whom.

## 🧠 How It Works
The script uses a **backtracking algorithm** to find a valid combination that minimizes penalties according to predefined rules.

## 🛠 Requirements
- Python 3.8+
- `openpyxl` library

Install dependencies with:
```bash
pip install openpyxl
```

## ▶️ Usage

Run the script:
```bash
python family_secret_santa.py
```

After execution:

The assignments are printed in the console.

An Excel file Secret_Santa_Result.xlsx is generated in the same folder.

## 📊 Example Output

---- Who gives to whom ----
Jonathan gives to child Noah and to adult Laura
...
Results exported to Secret_Santa_Result.xlsx

## 📁 Output Files
| File | Description |
|------|-------------|
| Secret_Santa_Result.xlsx | Contains the final gift exchange list |
