"""Budget calculations (no AI here - pure pandas)."""
import pandas as pd

COLUMNS = ["date", "description", "category", "amount", "type"]
CATEGORIES = ["Housing", "Food", "Transport", "Utilities", "Entertainment",
              "Shopping", "Health", "Education", "Savings", "Other"]


def empty_df() -> pd.DataFrame:
    return pd.DataFrame(columns=COLUMNS)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    df["type"] = df["type"].str.lower().fillna("expense")
    return df.dropna(subset=["date"])


def add_entry(df, date, description, category, amount, typ):
    row = pd.DataFrame([[pd.to_datetime(date), description, category, amount, typ]],
                       columns=COLUMNS)
    return pd.concat([df, row], ignore_index=True)


def summarize(df: pd.DataFrame) -> dict:
    income = df.loc[df["type"] == "income", "amount"].sum()
    expense = df.loc[df["type"] == "expense", "amount"].sum()
    by_cat = (df[df["type"] == "expense"].groupby("category")["amount"]
              .sum().sort_values(ascending=False).to_dict())
    savings = income - expense
    rate = (savings / income * 100) if income else 0
    return {
        "income": float(income),
        "expense": float(expense),
        "savings": float(savings),
        "savings_rate": round(float(rate), 1),
        "by_category": {k: float(v) for k, v in by_cat.items()},
    }


def rule_50_30_20(summary: dict) -> dict:
    """Compare spending with the 50/30/20 rule."""
    inc = summary["income"] or 1
    needs = sum(summary["by_category"].get(c, 0) for c in ["Housing", "Food", "Utilities", "Transport", "Health"])
    wants = sum(summary["by_category"].get(c, 0) for c in ["Entertainment", "Shopping", "Other"])
    return {
        "needs_pct": round(needs / inc * 100, 1),
        "wants_pct": round(wants / inc * 100, 1),
        "savings_pct": round(summary["savings"] / inc * 100, 1),
    }