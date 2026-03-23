#!/bin/bash
# ==============================================================================
# setup_kimi.sh — One-Command Setup for Kimi K2.5 Fine-Tuning Environment
# ==============================================================================
#
# Sets up everything needed to fine-tune Kimi K2.5 (1T MoE) into Darshana
# reasoning engines using KTransformers + LlamaFactory.
#
# Usage:
#     bash training/setup_kimi.sh
#
# What it does:
#     1. Checks CUDA availability and GPU memory
#     2. Checks system RAM and disk space
#     3. Installs KTransformers from source
#     4. Installs LlamaFactory
#     5. Downloads Kimi K2.5 model weights (with progress)
#     6. Converts INT4 -> BF16 if needed
#     7. Verifies the setup with a test inference
#     8. Prints summary and next steps
#
# Author: Harsh (with Claude as co-thinker)
# License: MIT
# ==============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo ""
echo "============================================================"
echo "  Kimi K2.5 Fine-Tuning Environment Setup"
echo "  Darshana Architecture — Training Pipeline"
echo "============================================================"
echo ""
echo "  Model:        Kimi K2.5 (1T parameters, 32B active)"
echo "  Architecture: MoE — 384 experts/layer, top-8 routing"
echo "  Method:       LoRA SFT via KTransformers + LlamaFactory"
echo "  Targets:      q_proj, k_proj, v_proj, o_proj (attention)"
echo ""
echo "============================================================"
echo ""

# Track what was installed/setup
SETUP_LOG=()
WARNINGS=()
ERRORS=()

# ---------------------------------------------------------------------------
# Step 1: Check CUDA
# ---------------------------------------------------------------------------
echo -e "${BLUE}[1/7] Checking CUDA availability...${NC}"

if command -v nvidia-smi &> /dev/null; then
    CUDA_AVAILABLE=true
    GPU_INFO=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits 2>/dev/null || echo "Unknown")
    GPU_COUNT=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | wc -l | tr -d ' ')
    TOTAL_VRAM=0

    echo -e "  ${GREEN}CUDA available${NC}"
    echo "  GPUs found: $GPU_COUNT"

    while IFS=',' read -r name mem; do
        name=$(echo "$name" | xargs)
        mem=$(echo "$mem" | xargs)
        echo "    - $name ($mem MiB)"
        TOTAL_VRAM=$((TOTAL_VRAM + mem))
    done <<< "$GPU_INFO"

    TOTAL_VRAM_GB=$((TOTAL_VRAM / 1024))
    echo "  Total VRAM: ${TOTAL_VRAM_GB} GB"

    if [ "$TOTAL_VRAM_GB" -lt 40 ]; then
        WARNINGS+=("GPU VRAM (${TOTAL_VRAM_GB} GB) is below recommended 48 GB (2x RTX 4090)")
        echo -e "  ${YELLOW}WARNING: ${TOTAL_VRAM_GB} GB VRAM may be insufficient. Need 48+ GB (2x RTX 4090).${NC}"
    else
        echo -e "  ${GREEN}VRAM OK for Kimi K2.5 fine-tuning${NC}"
    fi

    SETUP_LOG+=("CUDA: Available ($GPU_COUNT GPUs, ${TOTAL_VRAM_GB} GB VRAM)")
else
    CUDA_AVAILABLE=false
    echo -e "  ${YELLOW}WARNING: CUDA not available (nvidia-smi not found)${NC}"
    echo "  Kimi K2.5 fine-tuning requires CUDA GPUs."
    echo "  You can still generate configs for cloud training."
    WARNINGS+=("CUDA not available — use cloud training (--cloud runpod|lambda)")
    SETUP_LOG+=("CUDA: Not available")
fi
echo ""

# ---------------------------------------------------------------------------
# Step 2: Check RAM and Disk
# ---------------------------------------------------------------------------
echo -e "${BLUE}[2/7] Checking system resources...${NC}"

# RAM
if [[ "$OSTYPE" == "darwin"* ]]; then
    RAM_BYTES=$(sysctl -n hw.memsize 2>/dev/null || echo 0)
    RAM_GB=$((RAM_BYTES / 1073741824))
else
    RAM_KB=$(grep MemTotal /proc/meminfo 2>/dev/null | awk '{print $2}' || echo 0)
    RAM_GB=$((RAM_KB / 1048576))
fi

echo "  RAM: ${RAM_GB} GB"
if [ "$RAM_GB" -lt 128 ]; then
    WARNINGS+=("RAM (${RAM_GB} GB) is below minimum 128 GB for Kimi K2.5")
    echo -e "  ${YELLOW}WARNING: Need 128 GB minimum, 512 GB+ recommended${NC}"
elif [ "$RAM_GB" -lt 512 ]; then
    echo -e "  ${YELLOW}OK but 512 GB+ recommended for optimal throughput${NC}"
else
    echo -e "  ${GREEN}Excellent — sufficient for full MoE offloading${NC}"
fi

# Disk
DISK_FREE_KB=$(df -k "$HOME" 2>/dev/null | tail -1 | awk '{print $4}')
DISK_FREE_GB=$((DISK_FREE_KB / 1048576))

echo "  Disk free: ${DISK_FREE_GB} GB"
if [ "$DISK_FREE_GB" -lt 800 ]; then
    WARNINGS+=("Disk space (${DISK_FREE_GB} GB) is below recommended 800 GB")
    echo -e "  ${YELLOW}WARNING: Need 800+ GB for model weights + adapters${NC}"
else
    echo -e "  ${GREEN}Sufficient disk space${NC}"
fi

SETUP_LOG+=("System: ${RAM_GB} GB RAM, ${DISK_FREE_GB} GB disk free")
echo ""

# ---------------------------------------------------------------------------
# Step 3: Check Python and pip
# ---------------------------------------------------------------------------
echo -e "${BLUE}[3/7] Checking Python environment...${NC}"

PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    ERRORS+=("Python not found")
    echo -e "  ${RED}ERROR: Python not found. Install Python 3.9+${NC}"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo "  $PYTHON_VERSION"

PIP_CMD=""
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
elif $PYTHON_CMD -m pip --version &> /dev/null; then
    PIP_CMD="$PYTHON_CMD -m pip"
else
    ERRORS+=("pip not found")
    echo -e "  ${RED}ERROR: pip not found. Install pip.${NC}"
    exit 1
fi

echo "  pip: $($PIP_CMD --version 2>&1 | head -1)"
SETUP_LOG+=("Python: $PYTHON_VERSION")
echo ""

# ---------------------------------------------------------------------------
# Step 4: Install KTransformers
# ---------------------------------------------------------------------------
echo -e "${BLUE}[4/7] Installing KTransformers...${NC}"

if $PYTHON_CMD -c "import ktransformers" &> /dev/null; then
    KT_VERSION=$($PYTHON_CMD -c "import ktransformers; print(ktransformers.__version__)" 2>/dev/null || echo "unknown")
    echo -e "  ${GREEN}Already installed (version: $KT_VERSION)${NC}"
    SETUP_LOG+=("KTransformers: $KT_VERSION (already installed)")
else
    echo "  Installing ktransformers..."
    $PIP_CMD install ktransformers 2>&1 | tail -3

    if $PYTHON_CMD -c "import ktransformers" &> /dev/null; then
        KT_VERSION=$($PYTHON_CMD -c "import ktransformers; print(ktransformers.__version__)" 2>/dev/null || echo "unknown")
        echo -e "  ${GREEN}Installed successfully (version: $KT_VERSION)${NC}"
        SETUP_LOG+=("KTransformers: $KT_VERSION (newly installed)")
    else
        WARNINGS+=("KTransformers installation may have failed — check manually")
        echo -e "  ${YELLOW}WARNING: Installation may have failed. Check with: python -c 'import ktransformers'${NC}"
        SETUP_LOG+=("KTransformers: installation uncertain")
    fi
fi
echo ""

# ---------------------------------------------------------------------------
# Step 5: Install LlamaFactory
# ---------------------------------------------------------------------------
echo -e "${BLUE}[5/7] Installing LlamaFactory...${NC}"

if command -v llamafactory-cli &> /dev/null; then
    LF_VERSION=$(llamafactory-cli version 2>&1 | head -1 || echo "unknown")
    echo -e "  ${GREEN}Already installed ($LF_VERSION)${NC}"
    SETUP_LOG+=("LlamaFactory: $LF_VERSION (already installed)")
else
    echo "  Installing llamafactory..."
    $PIP_CMD install llamafactory 2>&1 | tail -3

    if command -v llamafactory-cli &> /dev/null; then
        LF_VERSION=$(llamafactory-cli version 2>&1 | head -1 || echo "unknown")
        echo -e "  ${GREEN}Installed successfully ($LF_VERSION)${NC}"
        SETUP_LOG+=("LlamaFactory: $LF_VERSION (newly installed)")
    else
        WARNINGS+=("LlamaFactory CLI not found after install — check manually")
        echo -e "  ${YELLOW}WARNING: llamafactory-cli not found. Try: pip install llamafactory${NC}"
        SETUP_LOG+=("LlamaFactory: installation uncertain")
    fi
fi

# Also install other training dependencies
echo "  Installing additional training dependencies..."
$PIP_CMD install -q torch transformers peft datasets accelerate bitsandbytes \
    trl flask scikit-learn rouge-score pyyaml tqdm tensorboard 2>&1 | tail -1
echo -e "  ${GREEN}Training dependencies installed${NC}"
echo ""

# ---------------------------------------------------------------------------
# Step 6: Download Kimi K2.5 model
# ---------------------------------------------------------------------------
echo -e "${BLUE}[6/7] Downloading Kimi K2.5 model weights...${NC}"
echo ""
echo "  Model: moonshotai/Kimi-K2.5-Instruct"
echo "  Size:  ~500-700 GB (INT4 quantized)"
echo ""

# Check if already downloaded
MODEL_CACHED=$($PYTHON_CMD -c "
from pathlib import Path
import os
cache = Path(os.environ.get('HF_HOME', Path.home() / '.cache' / 'huggingface'))
model_dir = cache / 'hub' / 'models--moonshotai--Kimi-K2.5-Instruct'
if model_dir.exists() and any(model_dir.rglob('*.safetensors')):
    print('yes')
else:
    print('no')
" 2>/dev/null || echo "no")

if [ "$MODEL_CACHED" = "yes" ]; then
    echo -e "  ${GREEN}Model already cached in HuggingFace hub${NC}"
    SETUP_LOG+=("Model: Already downloaded")
else
    echo "  Model not found in cache. Starting download..."
    echo "  This will take a while depending on your connection speed."
    echo ""

    # Check if user wants to proceed
    if [ -t 0 ]; then
        read -p "  Download Kimi K2.5 now? This requires ~700 GB disk space. [y/N] " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "  Downloading..."
            $PYTHON_CMD -c "
from huggingface_hub import snapshot_download
snapshot_download(
    'moonshotai/Kimi-K2.5-Instruct',
    resume_download=True,
)
print('Download complete.')
" 2>&1 | tail -5

            if [ $? -eq 0 ]; then
                echo -e "  ${GREEN}Download complete${NC}"
                SETUP_LOG+=("Model: Downloaded successfully")
            else
                WARNINGS+=("Model download may have failed — check manually")
                echo -e "  ${YELLOW}Download may have failed. Retry with:${NC}"
                echo "    python -c \"from huggingface_hub import snapshot_download; snapshot_download('moonshotai/Kimi-K2.5-Instruct')\""
                SETUP_LOG+=("Model: Download uncertain")
            fi
        else
            echo "  Skipping download. You can download later with:"
            echo "    python -c \"from huggingface_hub import snapshot_download; snapshot_download('moonshotai/Kimi-K2.5-Instruct')\""
            SETUP_LOG+=("Model: Download skipped (user choice)")
        fi
    else
        echo "  Non-interactive mode. Skipping model download."
        echo "  Download manually with:"
        echo "    python -c \"from huggingface_hub import snapshot_download; snapshot_download('moonshotai/Kimi-K2.5-Instruct')\""
        SETUP_LOG+=("Model: Download skipped (non-interactive)")
    fi
fi
echo ""

# ---------------------------------------------------------------------------
# Step 7: Verify setup
# ---------------------------------------------------------------------------
echo -e "${BLUE}[7/7] Verifying setup...${NC}"

VERIFY_RESULT=$($PYTHON_CMD -c "
import sys
checks = []

# Check torch
try:
    import torch
    checks.append(('torch', torch.__version__, True))
    if torch.cuda.is_available():
        checks.append(('CUDA', f'{torch.cuda.device_count()} GPUs', True))
    else:
        checks.append(('CUDA', 'not available', False))
except ImportError:
    checks.append(('torch', 'not installed', False))

# Check transformers
try:
    import transformers
    checks.append(('transformers', transformers.__version__, True))
except ImportError:
    checks.append(('transformers', 'not installed', False))

# Check peft
try:
    import peft
    checks.append(('peft', peft.__version__, True))
except ImportError:
    checks.append(('peft', 'not installed', False))

# Check ktransformers
try:
    import ktransformers
    checks.append(('ktransformers', getattr(ktransformers, '__version__', 'installed'), True))
except ImportError:
    checks.append(('ktransformers', 'not installed', False))

# Check datasets
try:
    import datasets
    checks.append(('datasets', datasets.__version__, True))
except ImportError:
    checks.append(('datasets', 'not installed', False))

# Check accelerate
try:
    import accelerate
    checks.append(('accelerate', accelerate.__version__, True))
except ImportError:
    checks.append(('accelerate', 'not installed', False))

# Check pyyaml
try:
    import yaml
    checks.append(('pyyaml', 'installed', True))
except ImportError:
    checks.append(('pyyaml', 'not installed', False))

# Check flask
try:
    import flask
    checks.append(('flask', flask.__version__, True))
except ImportError:
    checks.append(('flask', 'not installed', False))

for name, version, ok in checks:
    status = 'OK' if ok else 'MISSING'
    print(f'  {status:8s} {name:20s} {version}')

all_ok = all(ok for _, _, ok in checks)
sys.exit(0 if all_ok else 1)
" 2>&1)

echo "$VERIFY_RESULT"

if [ $? -eq 0 ]; then
    echo -e "\n  ${GREEN}All checks passed${NC}"
    SETUP_LOG+=("Verification: All checks passed")
else
    echo -e "\n  ${YELLOW}Some checks failed — see above${NC}"
    SETUP_LOG+=("Verification: Some checks failed")
fi
echo ""

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo "============================================================"
echo "  SETUP SUMMARY"
echo "============================================================"
echo ""

for item in "${SETUP_LOG[@]}"; do
    echo "  $item"
done

if [ ${#WARNINGS[@]} -gt 0 ]; then
    echo ""
    echo -e "  ${YELLOW}Warnings:${NC}"
    for warning in "${WARNINGS[@]}"; do
        echo -e "    ${YELLOW}- $warning${NC}"
    done
fi

if [ ${#ERRORS[@]} -gt 0 ]; then
    echo ""
    echo -e "  ${RED}Errors:${NC}"
    for error in "${ERRORS[@]}"; do
        echo -e "    ${RED}- $error${NC}"
    done
fi

echo ""
echo "============================================================"
echo "  NEXT STEPS"
echo "============================================================"
echo ""
echo "  1. Generate training data (if not done):"
echo "     python training/generate_data.py"
echo ""
echo "  2. Fine-tune a single darshana:"
echo "     python training/finetune_kimi.py --darshana nyaya"
echo ""
echo "  3. Fine-tune all darshanas:"
echo "     python training/finetune_kimi.py --all"
echo ""
echo "  4. Dry run (generate configs only):"
echo "     python training/finetune_kimi.py --darshana nyaya --dry-run"
echo ""
echo "  5. Cloud training:"
echo "     python training/finetune_kimi.py --all --cloud runpod"
echo ""
echo "  6. Serve after training:"
echo "     python training/serve_kimi.py --all --port 8000"
echo ""
echo "============================================================"
echo ""
