# =============================================================================
# Darshana Architecture — Developer Makefile
# =============================================================================
#
# Usage:
#   make install     Install package in dev mode
#   make test        Run all tests
#   make benchmark   Run performance benchmarks
#   make demo        Run all demos in sequence
#   make lint        Basic code quality checks
#   make clean       Remove temp files and caches
#   make run         Start the Darshana CLI
#   make setup       Run the full setup script
#   make help        Show this help
#
# =============================================================================

.PHONY: install test benchmark demo lint clean run setup help

PYTHON ?= python3
PIP    ?= pip

# ---------------------------------------------------------------------------
# Default target
# ---------------------------------------------------------------------------
help:
	@echo ""
	@echo "  Darshana Architecture — Developer Commands"
	@echo "  ==========================================="
	@echo ""
	@echo "  make install     Install package in editable mode with dev deps"
	@echo "  make test        Run pytest test suite"
	@echo "  make benchmark   Run router and filter benchmarks"
	@echo "  make demo        Run all demo scripts in sequence"
	@echo "  make lint        Run basic code quality checks"
	@echo "  make clean       Remove __pycache__, .egg-info, temp files"
	@echo "  make run         Launch the Darshana CLI (interactive help)"
	@echo "  make setup       Run the one-command setup script"
	@echo "  make db-reset    Reset SQLite databases (smriti + shakti)"
	@echo ""

# ---------------------------------------------------------------------------
# Installation
# ---------------------------------------------------------------------------
install:
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	@echo ""
	@echo "  Installed darshana in editable mode with dev dependencies."
	@echo "  Run 'make test' to verify everything works."
	@echo ""

# ---------------------------------------------------------------------------
# Testing
# ---------------------------------------------------------------------------
test:
	$(PYTHON) -m pytest tests/ -v --tb=short

test-quick:
	$(PYTHON) -m pytest tests/ -v --tb=short -x -q

# ---------------------------------------------------------------------------
# Benchmarks
# ---------------------------------------------------------------------------
benchmark:
	@echo "=== Router Benchmark ==="
	$(PYTHON) tests/benchmark.py
	@echo ""
	@echo "=== Filter Benchmark ==="
	$(PYTHON) tests/benchmark_filter.py

# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------
demo:
	@echo "=== Darshana Router Demo ==="
	$(PYTHON) -m src.demo
	@echo ""
	@echo "=== Vritti Filter Demo ==="
	$(PYTHON) -m src.demo_filter
	@echo ""
	@echo "=== Smriti (Memory) Demo ==="
	$(PYTHON) -m src.demo_smriti
	@echo ""
	@echo "=== Shakti (Compute) Demo ==="
	$(PYTHON) -m src.demo_shakti
	@echo ""
	@echo "=== Manas (Attention) Demo ==="
	$(PYTHON) -m src.demo_manas
	@echo ""
	@echo "=== Ahamkara (Self-Model) Demo ==="
	$(PYTHON) -m src.demo_ahamkara
	@echo ""
	@echo "=== Pratyaksha (Perception) Demo ==="
	$(PYTHON) -m src.demo_pratyaksha
	@echo ""
	@echo "=== Antahkarana (Full Pipeline) Demo ==="
	$(PYTHON) -m src.demo_antahkarana
	@echo ""
	@echo "=== Yaksha Protocol Demo ==="
	$(PYTHON) -m src.demo_yaksha

demo-router:
	$(PYTHON) -m src.demo

demo-filter:
	$(PYTHON) -m src.demo_filter

demo-smriti:
	$(PYTHON) -m src.demo_smriti

demo-shakti:
	$(PYTHON) -m src.demo_shakti

demo-antahkarana:
	$(PYTHON) -m src.demo_antahkarana

# ---------------------------------------------------------------------------
# Lint / Quality
# ---------------------------------------------------------------------------
lint:
	@echo "=== Syntax check ==="
	$(PYTHON) -m py_compile src/__init__.py
	$(PYTHON) -m py_compile src/__main__.py
	$(PYTHON) -m py_compile src/darshana_router.py
	$(PYTHON) -m py_compile src/vritti_filter.py
	$(PYTHON) -m py_compile src/darshana_llm.py
	$(PYTHON) -m py_compile src/antahkarana.py
	$(PYTHON) -m py_compile src/smriti.py
	$(PYTHON) -m py_compile src/shakti.py
	$(PYTHON) -m py_compile src/manas.py
	$(PYTHON) -m py_compile src/ahamkara.py
	$(PYTHON) -m py_compile src/pratyaksha.py
	$(PYTHON) -m py_compile src/yaksha.py
	$(PYTHON) -m py_compile src/prompts.py
	@echo ""
	@echo "  All modules compile cleanly."

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
run:
	$(PYTHON) -m darshana

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
setup:
	bash setup.sh

# ---------------------------------------------------------------------------
# Database reset
# ---------------------------------------------------------------------------
db-reset:
	@echo "Resetting Darshana databases..."
	rm -f ~/.darshana/db/smriti.db
	rm -f ~/.darshana/db/shakti_ledger.db
	@echo "Run 'bash setup.sh' or 'make setup' to reinitialize."

# ---------------------------------------------------------------------------
# Clean
# ---------------------------------------------------------------------------
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/ .eggs/
	@echo "  Cleaned."
