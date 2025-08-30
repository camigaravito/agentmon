set -euo pipefail

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m"

if ! command -v git >/dev/null 2>&1; then
  echo -e "${RED}[x] git no encontrado en el sistema${NC}"
  exit 1
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  echo -e "${RED}[x] No se encontró el remoto 'origin'. Configure con:${NC}"
  echo "   git remote add origin git@github.com:camigaravito/agentmon.git"
  exit 1
fi

current_branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)"
if [ "$current_branch" != "main" ]; then
  echo -e "${YELLOW}[i] Cambiando a rama 'main' desde '$current_branch'...${NC}"
  git checkout main 2>/dev/null || git switch main 2>/dev/null || {
    echo -e "${RED}[x] No existe la rama 'main'. Cree o renombre con:${NC}"
    echo "   git branch -M main"
    exit 1
  }
fi

echo -e "${YELLOW}[i] Estado del repositorio:${NC}"
git status --short

echo
read -rp "Escriba el mensaje de commit (o deje vacío para cancelar): " COMMIT_MSG
if [ -z "${COMMIT_MSG}" ]; then
  echo -e "${RED}[x] Commit cancelado: mensaje vacío${NC}"
  exit 1
fi

echo -e "${YELLOW}[i] Agregando cambios...${NC}"
git add -A

if git diff --cached --quiet; then
  echo -e "${YELLOW}[i] No hay cambios staged para commit. Saliendo.${NC}"
  exit 0
fi

git commit -m "${COMMIT_MSG}"

echo -e "${YELLOW}[i] Sincronizando con origin/main (pull --rebase)...${NC}"
git pull --rebase origin main || {
  echo -e "${RED}[x] Conflictos durante rebase. Resuelva y ejecute de nuevo:${NC}"
  echo "   git rebase --continue   (o --abort)"
  exit 1
}

echo -e "${YELLOW}[i] Pushing a origin/main...${NC}"
git push origin main

echo -e "${GREEN}[✓] Sincronización completada con éxito.${NC}"