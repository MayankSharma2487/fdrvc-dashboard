"""
refresh_data.py
===============
Run this script manually (or via GitHub Actions / cron) to
download fresh data from the MIS portal and save as Parquet.

Usage:
    python refresh_data.py

The dashboard reads from data/parquet/ — NOT from this script.
"""

import os
import io
import time
import requests
import pandas as pd
from datetime import datetime
from utils.constants import REPORT_URLS

RAW_DIR     = "data/raw"
PARQUET_DIR = "data/parquet"

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PARQUET_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,*/*",
    "Accept-Language": "en-US,en;q=0.9",
}

def download_with_retry(name, url, retries=3, delay=10):
    """Download a URL with retry logic. Returns bytes or None."""
    for attempt in range(1, retries + 1):
        try:
            print(f"  [{attempt}/{retries}] Downloading {name}...")
            r = requests.get(url, headers=HEADERS, timeout=120)
            r.raise_for_status()

            # Detect HTML error page from BIRT
            ct = r.headers.get("Content-Type", "")
            if "html" in ct.lower() and len(r.content) < 50_000:
                print(f"  ⚠️  {name}: Server returned HTML (session/auth issue), skipping.")
                return None

            return r.content

        except requests.exceptions.Timeout:
            print(f"  ⏱  {name}: Timeout on attempt {attempt}")
        except requests.exceptions.ConnectionError as e:
            print(f"  🔌  {name}: Connection error on attempt {attempt}: {e}")
        except Exception as e:
            print(f"  ❌  {name}: Error on attempt {attempt}: {e}")

        if attempt < retries:
            print(f"  ⏳  Retrying in {delay}s...")
            time.sleep(delay)

    return None


def save_as_parquet(name, content):
    """Parse Excel bytes → clean DataFrame → save as Parquet."""
    try:
        df = pd.read_excel(io.BytesIO(content), engine="openpyxl")

        # Clean column names
        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.replace("\n", " ", regex=False)
            .str.replace("  ", " ", regex=False)
        )

        # Keep monetary/numeric columns as float64 to avoid rounding errors.
        # Only downcast small non-monetary float columns if needed for memory.
        # Commented out the blanket float64→float32 downcast that caused ~₹0.2 Cr
        # discrepancies in EG and MC totals due to accumulated float32 precision loss.
        #
        # for col in df.select_dtypes(include=["float64"]).columns:
        #     df[col] = pd.to_numeric(df[col], errors="coerce").astype("float32")

        # Convert ONLY pure low-cardinality string columns to category.
        # Skip any column that has mixed types (int/float values mixed with strings)
        # — this is the BIRT "header row embedded in data" pattern.
        for col in df.select_dtypes(include=["object", "str"]).columns:
            series = df[col].dropna()
            if series.empty:
                continue
            n_unique = series.nunique()
            n_total  = len(series)
            # Only categorize if: low cardinality AND all values are actual strings
            # (not numbers stored as object due to mixed types)
            if n_unique < 200 and n_total > 500:
                # Check if any values are numeric — if so, skip category conversion
                has_numeric = pd.to_numeric(series, errors="coerce").notna().any()
                if not has_numeric:
                    df[col] = df[col].astype("category")

        parquet_path = os.path.join(PARQUET_DIR, f"{name}.parquet")
        df.to_parquet(parquet_path, index=False, compression="snappy")
        print(f"  ✅  {name}: {len(df)} rows → {parquet_path}")
        return True

    except Exception as e:
        print(f"  ❌  {name}: Failed to parse/save parquet: {e}")
        return False


def main():
    print(f"\n{'='*60}")
    print(f"FDRVC MIS Data Refresh — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    success_count = 0
    fail_list = []

    for name, url in REPORT_URLS.items():
        print(f"\n📥  {name}")

        content = download_with_retry(name, url)

        if content is None:
            fail_list.append(name)
            continue

        # Save raw Excel backup
        raw_path = os.path.join(RAW_DIR, f"{name}.xlsx")
        with open(raw_path, "wb") as f:
            f.write(content)

        # Convert to Parquet
        ok = save_as_parquet(name, content)
        if ok:
            success_count += 1
        else:
            fail_list.append(name)

        # Small delay to be polite to the server
        time.sleep(2)

    # Write refresh timestamp
    with open("data/last_refresh.txt", "w") as f:
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    print(f"\n{'='*60}")
    print(f"✅  Success: {success_count}/{len(REPORT_URLS)} reports")
    if fail_list:
        print(f"❌  Failed:  {', '.join(fail_list)}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()