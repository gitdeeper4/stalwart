# STALWART Installation Guide

## Prerequisites
- Python 3.9 or later
- pip (Python package manager)
- virtualenv (recommended)

## Quick Installation

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/stalwart.git
cd stalwart
```

2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. Install Required Packages

```bash
pip install -e .
```

4. Install Development Packages (Optional)

```bash
pip install -e .[dev]
```

5. Verify Installation

```bash
python -c "import stalwart; print(stalwart.__version__)"
```

Development Installation

```bash
# Clone repository
git clone https://github.com/yourusername/stalwart.git
cd stalwart

# Install with development packages
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/
```

Hardware Requirements (For Field Deployment)

Sensors (Per Measurement Point)

· Strain gauges - I2C/SPI interface
· Accelerometers - I2C interface
· Acoustic sensors - USB/Analog interface
· Thermal sensors - 1-Wire interface
· Corrosion sensors - I2C/RS485 interface

Field Data Acquisition Unit

· Raspberry Pi 4 or higher
· Arduino Due (for direct reading)
· Backup battery
· 4G/LTE or fiber optic connection

Central Server

· 8+ CPU cores
· 32+ GB RAM
· 1+ TB storage
· Linux OS (Ubuntu 22.04 LTS)

Troubleshooting

Issue: numpy installation fails

Solution: Upgrade pip

```bash
pip install --upgrade pip
```

Issue: Python version conflict

Solution: Use pyenv to manage versions

```bash
pyenv install 3.11.0
pyenv local 3.11.0
```

Support

· Open an Issue on GitHub for problems
· Check documentation in docs/
· Contact the development team

---

Last updated: February 16, 2026

### Repository Access

Clone the project from any of these mirrors:

```bash
# GitLab
git clone https://gitlab.com/gitdeeper4/stalwart.git

# GitHub
git clone https://github.com/gitdeeper4/stalwart.git

# Codeberg
git clone https://codeberg.org/gitdeeper4/stalwart.git

# Bitbucket
git clone https://bitbucket.org/gitdeeper7/stalwart.git
```

