#!/usr/bin/env bash
# scripts/setup-creds.sh — одноразовая настройка кред для RCI API Keenetic.
# Запускать В СВОЁМ терминале (не в чате агенту): пароль вводится скрыто и
# сохраняется в ~/.config/keenetic/api.netrc (chmod 600, вне репозитория).
# Агент затем работает через scripts/rci.sh / curl --netrc-file, секрет не видит.
# Повторный запуск перезаписывает файл (например, при смене пароля на роутере).
set -euo pipefail

HOST="${KEENETIC_HOST:-192.168.1.1}"
LOGIN="${KEENETIC_USER:-admin}"
NETRC_DIR="$HOME/.config/keenetic"
NETRC="$NETRC_DIR/api.netrc"

read -rp "Host роутера [$HOST]: " H; HOST="${H:-$HOST}"
read -rp "Логин [$LOGIN]: " U; LOGIN="${U:-$LOGIN}"

while true; do
  IFS= read -rsp "Пароль ${LOGIN}@${HOST}: " P; echo
  IFS= read -rsp "Повторите пароль: " P2; echo
  [[ "$P" == "$P2" ]] && break
  echo "Пароли не совпадают, попробуйте ещё раз." >&2
done

mkdir -p "$NETRC_DIR"
chmod 700 "$NETRC_DIR"
umask 177   # файл создаётся с правами rw-только-владельцу
printf 'machine %s\nlogin %s\npassword %s\n' "$HOST" "$LOGIN" "$P" > "$NETRC"
unset P P2
chmod 600 "$NETRC"

if command -v curl >/dev/null; then
  echo "Проверка авторизации (rci/show/version)..."
  if OUT=$(curl -sfS --netrc-file "$NETRC" "http://${HOST}/rci/show/version"); then
    echo "$OUT"
    echo "OK: $NETRC создан, авторизация работает."
  else
    echo "ВНИМАНИЕ: файл создан, но проверка не прошла (роутер недоступен или пароль неверный)." >&2
    exit 1
  fi
fi
echo "Права: $(stat -c '%a' "$NETRC") на $NETRC"
