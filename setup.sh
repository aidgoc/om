#!/bin/bash
# =============================================================================
# Darshana Architecture — One-Command Setup
# =============================================================================
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/aidgoc/om/main/setup.sh | bash
#
# Or after cloning:
#   cd om && bash setup.sh
#
# What this does:
#   1. Checks Python 3.9+
#   2. Creates ~/.darshana/ directory structure
#   3. Creates a virtual environment at ~/.darshana/venv
#   4. Installs the darshana package
#   5. Creates default config.json
#   6. Initializes SQLite databases (smriti.db, shakti_ledger.db)
#   7. Optionally configures your Anthropic API key
#   8. Prints quick-start commands
#
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Colors and formatting
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'  # No color

info()    { echo -e "${CYAN}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC}   $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
error()   { echo -e "${RED}[ERR]${NC}  $*"; }

# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------
echo ""
echo -e "${BOLD}"
echo "  OM — The Darshana Architecture"
echo "  Hindu philosophical reasoning framework for AI"
echo -e "${NC}${DIM}"
echo "  Perceive -> Remember -> Assemble -> Route -> Reason -> Filter -> Learn -> Respond"
echo -e "${NC}"
echo ""

# ---------------------------------------------------------------------------
# Step 1: Check Python version
# ---------------------------------------------------------------------------
info "Checking Python version..."

PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        version=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
        major=$("$cmd" -c "import sys; print(sys.version_info.major)" 2>/dev/null || echo "0")
        minor=$("$cmd" -c "import sys; print(sys.version_info.minor)" 2>/dev/null || echo "0")
        if [ "$major" -ge 3 ] && [ "$minor" -ge 9 ]; then
            PYTHON="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    error "Python 3.9+ is required but not found."
    echo ""
    echo "  Install Python:"
    echo "    macOS:   brew install python@3.12"
    echo "    Ubuntu:  sudo apt install python3.12 python3.12-venv"
    echo "    Windows: https://www.python.org/downloads/"
    echo ""
    exit 1
fi

PYTHON_VERSION=$("$PYTHON" --version 2>&1)
success "Found $PYTHON_VERSION ($PYTHON)"

# ---------------------------------------------------------------------------
# Step 2: Create ~/.darshana/ directory
# ---------------------------------------------------------------------------
DARSHANA_HOME="$HOME/.darshana"

info "Creating Darshana home directory at $DARSHANA_HOME..."

mkdir -p "$DARSHANA_HOME"
mkdir -p "$DARSHANA_HOME/db"
mkdir -p "$DARSHANA_HOME/logs"
mkdir -p "$DARSHANA_HOME/cache"

success "Directory structure created"

# ---------------------------------------------------------------------------
# Step 3: Create virtual environment
# ---------------------------------------------------------------------------
VENV_DIR="$DARSHANA_HOME/venv"

if [ -d "$VENV_DIR" ] && [ -f "$VENV_DIR/bin/activate" ]; then
    info "Virtual environment already exists at $VENV_DIR"
else
    info "Creating virtual environment at $VENV_DIR..."
    "$PYTHON" -m venv "$VENV_DIR"
    success "Virtual environment created"
fi

# Activate it
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
success "Virtual environment activated"

# ---------------------------------------------------------------------------
# Step 4: Install the package
# ---------------------------------------------------------------------------
info "Installing Darshana..."

# Determine if we are inside the repo or need to clone
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"

if [ -f "$SCRIPT_DIR/pyproject.toml" ]; then
    # Running from inside the repo
    pip install --upgrade pip --quiet
    pip install -e "$SCRIPT_DIR" --quiet
    success "Installed from local repo ($SCRIPT_DIR)"
elif [ -d "./om" ] && [ -f "./om/pyproject.toml" ]; then
    pip install --upgrade pip --quiet
    pip install -e ./om --quiet
    success "Installed from ./om"
else
    # Clone and install
    info "Cloning repository..."
    git clone --depth 1 https://github.com/aidgoc/om.git "$DARSHANA_HOME/repo" 2>/dev/null || true
    pip install --upgrade pip --quiet
    pip install -e "$DARSHANA_HOME/repo" --quiet
    success "Cloned and installed"
fi

# ---------------------------------------------------------------------------
# Step 5: Create default config.json
# ---------------------------------------------------------------------------
CONFIG_FILE="$DARSHANA_HOME/config.json"

if [ -f "$CONFIG_FILE" ]; then
    info "Config already exists at $CONFIG_FILE — preserving"
else
    info "Creating default config..."
    cat > "$CONFIG_FILE" <<'CONFIGEOF'
{
    "version": "0.2.0",
    "anthropic": {
        "api_key": null,
        "default_model": "claude-sonnet-4-20250514",
        "max_tokens": 4096
    },
    "shakti": {
        "budget_daily_usd": 10.0,
        "budget_monthly_usd": 100.0,
        "rate_limit_rpm": 50,
        "model_tiers": {
            "sattva": "claude-sonnet-4-20250514",
            "rajas": "claude-sonnet-4-20250514",
            "tamas": "claude-haiku-4-20250514"
        }
    },
    "smriti": {
        "db_path": "~/.darshana/db/smriti.db",
        "max_samskaras": 10000,
        "decay_rate": 0.01
    },
    "manas": {
        "max_context_tokens": 8192,
        "relevance_threshold": 0.3
    },
    "logging": {
        "level": "INFO",
        "file": "~/.darshana/logs/darshana.log"
    }
}
CONFIGEOF
    success "Default config created at $CONFIG_FILE"
fi

# ---------------------------------------------------------------------------
# Step 6: Prompt for Anthropic API key (optional)
# ---------------------------------------------------------------------------
echo ""

# Check if already set in environment
if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    info "ANTHROPIC_API_KEY already set in environment"
elif [ -t 0 ]; then
    # Interactive terminal — prompt user
    echo -e "${CYAN}[OPTIONAL]${NC} Enter your Anthropic API key for LLM features."
    echo -e "${DIM}  (Press Enter to skip — all local features work without it)${NC}"
    echo -n "  API key: "
    read -r API_KEY

    if [ -n "$API_KEY" ]; then
        # Update config.json with the key
        "$PYTHON" -c "
import json
with open('$CONFIG_FILE', 'r') as f:
    cfg = json.load(f)
cfg['anthropic']['api_key'] = '$API_KEY'
with open('$CONFIG_FILE', 'w') as f:
    json.dump(cfg, f, indent=4)
"
        # Also suggest adding to shell profile
        success "API key saved to config"
        echo ""
        echo -e "  ${DIM}Tip: also export in your shell profile for CLI use:${NC}"
        echo -e "  ${BOLD}export ANTHROPIC_API_KEY=\"$API_KEY\"${NC}"
    else
        info "Skipped — you can add it later in $CONFIG_FILE"
    fi
else
    info "Non-interactive mode — skipping API key prompt"
    info "Set ANTHROPIC_API_KEY or edit $CONFIG_FILE later"
fi

# ---------------------------------------------------------------------------
# Step 7: Initialize SQLite databases
# ---------------------------------------------------------------------------
info "Initializing databases..."

"$PYTHON" -c "
import sqlite3, os

db_dir = os.path.expanduser('~/.darshana/db')

# Smriti — memory / samskaras
conn = sqlite3.connect(os.path.join(db_dir, 'smriti.db'))
conn.executescript('''
    CREATE TABLE IF NOT EXISTS samskaras (
        id TEXT PRIMARY KEY,
        query_hash TEXT NOT NULL,
        domain TEXT DEFAULT \"general\",
        content TEXT NOT NULL,
        samskara_type TEXT DEFAULT \"experience\",
        strength REAL DEFAULT 1.0,
        access_count INTEGER DEFAULT 0,
        created_at REAL NOT NULL,
        last_accessed REAL NOT NULL,
        metadata TEXT DEFAULT \"{}\"
    );
    CREATE INDEX IF NOT EXISTS idx_samskaras_domain ON samskaras(domain);
    CREATE INDEX IF NOT EXISTS idx_samskaras_type ON samskaras(samskara_type);
    CREATE INDEX IF NOT EXISTS idx_samskaras_strength ON samskaras(strength DESC);

    CREATE TABLE IF NOT EXISTS vasanas (
        id TEXT PRIMARY KEY,
        domain TEXT NOT NULL,
        pattern TEXT NOT NULL,
        weight REAL DEFAULT 0.0,
        trigger_count INTEGER DEFAULT 0,
        created_at REAL NOT NULL,
        last_triggered REAL NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_vasanas_domain ON vasanas(domain);
')
conn.close()

# Shakti — cost ledger
conn = sqlite3.connect(os.path.join(db_dir, 'shakti_ledger.db'))
conn.executescript('''
    CREATE TABLE IF NOT EXISTS calls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL NOT NULL,
        model TEXT NOT NULL,
        input_tokens INTEGER DEFAULT 0,
        output_tokens INTEGER DEFAULT 0,
        cost_usd REAL DEFAULT 0.0,
        darshana TEXT,
        guna TEXT,
        cached INTEGER DEFAULT 0,
        latency_ms REAL DEFAULT 0.0,
        metadata TEXT DEFAULT \"{}\"
    );
    CREATE INDEX IF NOT EXISTS idx_calls_timestamp ON calls(timestamp);
    CREATE INDEX IF NOT EXISTS idx_calls_model ON calls(model);

    CREATE TABLE IF NOT EXISTS daily_totals (
        date TEXT PRIMARY KEY,
        total_cost REAL DEFAULT 0.0,
        total_calls INTEGER DEFAULT 0,
        total_input_tokens INTEGER DEFAULT 0,
        total_output_tokens INTEGER DEFAULT 0
    );
')
conn.close()
"

success "Databases initialized (smriti.db, shakti_ledger.db)"

# ---------------------------------------------------------------------------
# Step 8: Welcome message
# ---------------------------------------------------------------------------
echo ""
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}  Darshana Architecture — Setup Complete${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""
echo -e "  ${BOLD}Quick Start:${NC}"
echo ""
echo -e "    ${CYAN}# Route a query through the six darshana engines${NC}"
echo -e "    darshana \"Is this argument logically valid?\""
echo ""
echo -e "    ${CYAN}# Multi-engine analysis (up to 3 perspectives)${NC}"
echo -e "    darshana --multi \"Should we rewrite our backend in Rust?\""
echo ""
echo -e "    ${CYAN}# Run with real LLM calls (requires API key)${NC}"
echo -e "    darshana --llm \"What is consciousness?\""
echo ""
echo -e "    ${CYAN}# Classify output quality with the Vritti Filter${NC}"
echo -e "    darshana --filter \"The moon is made of cheese\""
echo ""
echo -e "    ${CYAN}# Run the demos${NC}"
echo -e "    darshana --demo"
echo ""
echo -e "    ${CYAN}# Use as a Python library${NC}"
echo -e "    python -c \"from darshana import Antahkarana; print('ready')\""
echo ""
echo -e "  ${BOLD}Files:${NC}"
echo -e "    Config:   $CONFIG_FILE"
echo -e "    Memory:   $DARSHANA_HOME/db/smriti.db"
echo -e "    Ledger:   $DARSHANA_HOME/db/shakti_ledger.db"
echo -e "    Logs:     $DARSHANA_HOME/logs/"
echo -e "    Venv:     $VENV_DIR"
echo ""
echo -e "  ${BOLD}Shell alias (add to ~/.zshrc or ~/.bashrc):${NC}"
echo ""
echo -e "    alias darshana='$VENV_DIR/bin/python -m darshana'"
echo ""
echo -e "  ${DIM}ekam sat vipra bahudha vadanti${NC}"
echo -e "  ${DIM}Truth is one. The wise call it by many names. — Rig Veda 1.164.46${NC}"
echo ""
