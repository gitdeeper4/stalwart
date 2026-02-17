#!/usr/bin/env python3
"""Simple report generator without symlinks."""

import os
import shutil
from datetime import datetime
from pathlib import Path

# قوالب بسيطة
DAILY_TEMPLATE = """# STALWART Daily Report
Date: {date}
Bridge: TEST-001
Health: 94.7%
Status: SAFE
"""

WEEKLY_TEMPLATE = """# STALWART Weekly Report
Week: {week}
Bridge: TEST-001
Average Health: 93.5%
Trend: Stable
"""

MONTHLY_TEMPLATE = """# STALWART Monthly Report
Month: {month}
Bridge: TEST-001
Monthly Average: 94.2%
Recommendation: Continue monitoring
"""

def main():
    now = datetime.now()
    
    # Daily report
    daily_dir = Path(f"reports/daily/{now.strftime('%Y-%m-%d')}")
    daily_dir.mkdir(parents=True, exist_ok=True)
    
    with open(daily_dir / f"STW-D-{now.strftime('%Y%m%d')}-TEST-001.md", 'w') as f:
        f.write(DAILY_TEMPLATE.format(date=now.strftime('%Y-%m-%d')))
    print(f"✅ Daily report created in {daily_dir}")
    
    # Weekly report
    week = now.strftime('%Y-W%V')
    weekly_dir = Path(f"reports/weekly/{week}")
    weekly_dir.mkdir(parents=True, exist_ok=True)
    
    with open(weekly_dir / f"STW-W-{now.strftime('%Y%V')}-TEST-001.md", 'w') as f:
        f.write(WEEKLY_TEMPLATE.format(week=week))
    print(f"✅ Weekly report created in {weekly_dir}")
    
    # Monthly report
    month = now.strftime('%Y-%m')
    monthly_dir = Path(f"reports/monthly/{month}")
    monthly_dir.mkdir(parents=True, exist_ok=True)
    
    with open(monthly_dir / f"STW-M-{now.strftime('%Y%m')}-TEST-001.md", 'w') as f:
        f.write(MONTHLY_TEMPLATE.format(month=now.strftime('%B %Y')))
    print(f"✅ Monthly report created in {monthly_dir}")
    
    print("\n📊 All reports generated successfully!")

if __name__ == "__main__":
    main()
