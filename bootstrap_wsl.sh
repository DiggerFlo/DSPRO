#!/usr/bin/env bash
# =============================================================================
#  DSPRO — WSL Bootstrap Script
#  Laeuft innerhalb von Ubuntu (WSL) nach dem ersten Login.
#  Installiert alle System-Abhaengigkeiten und richtet das Repo ein.
#
#  Aufruf:
#    bash bootstrap_wsl.sh
#  Oder direkt per curl:
#    curl -fsSL https://raw.githubusercontent.com/<USER>/<REPO>/main/bootstrap_wsl.sh | bash
# =============================================================================

set -euo pipefail

# ── Farben ────────────────────────────────────────────────────────────────────
CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
step()  { echo -e "\n${CYAN}  >> $1${NC}"; }
ok()    { echo -e "  ${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "  ${YELLOW}[!]${NC}  $1"; }
fail()  { echo -e "  ${RED}[X]${NC}  $1"; exit 1; }

echo ""
echo "=================================================="
echo -e "${CYAN}   DSPRO — WSL Development Environment Setup${NC}"
echo "=================================================="
echo ""

# ── Repo-URL (anpassen oder beim Start setzen) ────────────────────────────────
REPO_URL="${DSPRO_REPO_URL:-}"
if [[ -z "$REPO_URL" ]]; then
    echo -e "${YELLOW}  Bitte die GitHub Repo-URL eingeben:${NC}"
    read -rp "  URL: " REPO_URL
fi
REPO_NAME=$(basename "$REPO_URL" .git)

# ── 1. System updaten ─────────────────────────────────────────────────────────
step "System aktualisieren..."
sudo apt-get update -qq
sudo apt-get upgrade -y -qq
ok "System ist aktuell."

# ── 2. System-Abhaengigkeiten installieren ────────────────────────────────────
step "Installiere System-Pakete..."
sudo apt-get install -y -qq \
    git \
    curl \
    wget \
    unzip \
    build-essential \
    python3 \
    python3-pip \
    python3-venv \
    python3-full \
    ca-certificates \
    gnupg \
    lsb-release

ok "System-Pakete installiert."

# ── 3. Python-Version pruefen ─────────────────────────────────────────────────
step "Pruefe Python-Version..."
PYTHON_VERSION=$(python3 --version 2>&1)
PYTHON_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
PYTHON_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")

if [[ "$PYTHON_MAJOR" -lt 3 || ("$PYTHON_MAJOR" -eq 3 && "$PYTHON_MINOR" -lt 10) ]]; then
    warn "Python $PYTHON_VERSION gefunden. Empfohlen: Python 3.10+."
    warn "Installiere Python 3.12 via deadsnakes PPA..."
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt-get update -qq
    sudo apt-get install -y -qq python3.12 python3.12-venv python3.12-dev
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1
    ok "Python 3.12 installiert."
else
    ok "$PYTHON_VERSION ist kompatibel."
fi

# ── 4. Git konfigurieren ──────────────────────────────────────────────────────
step "Git konfigurieren..."
GIT_NAME=$(git config --global user.name 2>/dev/null || echo "")
GIT_EMAIL=$(git config --global user.email 2>/dev/null || echo "")

if [[ -z "$GIT_NAME" ]]; then
    read -rp "  Git Name (z.B. Max Mustermann): " GIT_NAME
    git config --global user.name "$GIT_NAME"
fi
if [[ -z "$GIT_EMAIL" ]]; then
    read -rp "  Git E-Mail: " GIT_EMAIL
    git config --global user.email "$GIT_EMAIL"
fi

# Sinnvolle Git-Standardeinstellungen
git config --global init.defaultBranch main
git config --global pull.rebase false
git config --global core.autocrlf input   # Wichtig: Windows-Zeilenenden normalisieren in WSL

ok "Git konfiguriert als '$GIT_NAME <$GIT_EMAIL>'."

# ── 5. Repo klonen ─────────────────────────────────────────────────────────────
step "Klone Repository..."
TARGET_DIR="$HOME/$REPO_NAME"

if [[ -d "$TARGET_DIR/.git" ]]; then
    warn "Repo existiert bereits unter $TARGET_DIR — ueberspringe Clone."
else
    git clone "$REPO_URL" "$TARGET_DIR"
    ok "Repo geklont nach $TARGET_DIR."
fi

cd "$TARGET_DIR"

# ── 6. Projekt-Setup ausfuehren ───────────────────────────────────────────────
step "Fuehre setup.sh aus..."
bash setup.sh
ok "Projekt-Setup abgeschlossen."

# ── 7. VS Code WSL-Integration (optional) ─────────────────────────────────────
step "Pruefe VS Code..."
if command -v code &>/dev/null; then
    ok "VS Code CLI gefunden."
    warn "Installiere nuetzliche VS Code Extensions..."
    code --install-extension ms-python.python --force 2>/dev/null || true
    code --install-extension ms-toolsai.jupyter --force 2>/dev/null || true
else
    warn "VS Code CLI nicht gefunden."
    warn "Installiere VS Code auf Windows + die Extension 'WSL' (ms-vscode-remote.remote-wsl)."
    warn "Danach kannst du 'code .' im Terminal nutzen."
fi

# ── Fertig ────────────────────────────────────────────────────────────────────
echo ""
echo "=================================================="
echo -e "${GREEN}   Setup erfolgreich abgeschlossen!${NC}"
echo "=================================================="
echo ""
echo -e "  Naechste Schritte:"
echo ""
echo -e "  1. Umgebung aktivieren:   ${CYAN}cd $TARGET_DIR && source .venv/bin/activate${NC}"
echo -e "  2. .env anpassen:         ${CYAN}nano .env${NC}  (OpenAI API-Key eintragen)"
echo -e "  3. VS Code oeffnen:       ${CYAN}code .${NC}"
echo -e "  4. MLflow starten:        ${CYAN}mlflow ui --backend-store-uri experiments/mlflow${NC}"
echo -e "  5. Pipeline testen:       ${CYAN}python main.py --query 'Testfrage'${NC}"
echo ""
