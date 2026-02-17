#!/bin/bash
# STALWART Report Generator Script
# Auto-generates daily, weekly, and monthly reports

REPORTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_CMD="python3"
GENERATOR="$REPORTS_DIR/generator.py"
LOG_FILE="$REPORTS_DIR/generator.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check if Python is available
if ! command -v $PYTHON_CMD &> /dev/null; then
    log "${RED}ERROR: Python not found${NC}"
    exit 1
fi

# Check if generator exists
if [ ! -f "$GENERATOR" ]; then
    log "${RED}ERROR: Generator not found: $GENERATOR${NC}"
    exit 1
fi

# Function to generate daily report
generate_daily() {
    log "${YELLOW}Generating daily reports...${NC}"
    $PYTHON_CMD "$GENERATOR" --type daily --format both
    if [ $? -eq 0 ]; then
        log "${GREEN}✅ Daily reports generated successfully${NC}"
    else
        log "${RED}❌ Failed to generate daily reports${NC}"
    fi
}

# Function to generate weekly report (every Monday)
generate_weekly() {
    log "${YELLOW}Generating weekly reports...${NC}"
    $PYTHON_CMD "$GENERATOR" --type weekly --format both
    if [ $? -eq 0 ]; then
        log "${GREEN}✅ Weekly reports generated successfully${NC}"
    else
        log "${RED}❌ Failed to generate weekly reports${NC}"
    fi
}

# Function to generate monthly report (1st of month)
generate_monthly() {
    log "${YELLOW}Generating monthly reports...${NC}"
    $PYTHON_CMD "$GENERATOR" --type monthly --format both
    if [ $? -eq 0 ]; then
        log "${GREEN}✅ Monthly reports generated successfully${NC}"
    else
        log "${RED}❌ Failed to generate monthly reports${NC}"
    fi
}

# Function to archive old reports (monthly)
archive_reports() {
    log "${YELLOW}Archiving old reports...${NC}"
    $PYTHON_CMD "$GENERATOR" --archive 90
    if [ $? -eq 0 ]; then
        log "${GREEN}✅ Reports archived successfully${NC}"
    else
        log "${RED}❌ Failed to archive reports${NC}"
    fi
}

# Function to generate sample reports for testing
generate_samples() {
    log "${YELLOW}Generating sample reports...${NC}"
    $PYTHON_CMD "$GENERATOR" --sample --type all --format both
    if [ $? -eq 0 ]; then
        log "${GREEN}✅ Sample reports generated successfully${NC}"
        echo -e "\n${GREEN}Sample reports created in:${NC}"
        ls -la "$REPORTS_DIR"/{daily,weekly,monthly,alerts}/*/latest.* 2>/dev/null
    else
        log "${RED}❌ Failed to generate sample reports${NC}"
    fi
}

# Display help
show_help() {
    echo "STALWART Report Generator"
    echo "========================"
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  daily      Generate daily reports"
    echo "  weekly     Generate weekly reports"
    echo "  monthly    Generate monthly reports"
    echo "  all        Generate all report types"
    echo "  archive    Archive old reports (90+ days)"
    echo "  samples    Generate sample reports for testing"
    echo "  cron       Run scheduled generation (checks day of week/month)"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 daily     # Generate daily reports"
    echo "  $0 all       # Generate all report types"
    echo "  $0 samples   # Generate test samples"
}

# Main execution based on argument
case "${1:-help}" in
    daily)
        generate_daily
        ;;
    weekly)
        generate_weekly
        ;;
    monthly)
        generate_monthly
        ;;
    all)
        generate_daily
        generate_weekly
        generate_monthly
        ;;
    archive)
        archive_reports
        ;;
    samples)
        generate_samples
        ;;
    cron)
        # Run based on schedule
        DAY_OF_WEEK=$(date +%u)  # 1-7 (Monday=1)
        DAY_OF_MONTH=$(date +%d) # 01-31
        
        # Always generate daily
        generate_daily
        
        # Generate weekly on Mondays (day 1)
        if [ "$DAY_OF_WEEK" -eq 1 ]; then
            generate_weekly
        fi
        
        # Generate monthly on 1st of month
        if [ "$DAY_OF_MONTH" -eq 1 ]; then
            generate_monthly
            # Archive on 1st of month
            archive_reports
        fi
        ;;
    help|*)
        show_help
        ;;
esac

exit 0
