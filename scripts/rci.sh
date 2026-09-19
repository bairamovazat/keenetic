#!/usr/bin/env bash
# scripts/rci.sh — обёртка над RCI API Keenetic (192.168.1.1).
# Креды: если создан ~/.config/keenetic/api.netrc (chmod 600) — пароль не спрашивается,
# curl читает его сам (--netrc-file, пароль не светится в argv/истории).
# Иначе — интерактивный ввод (пароль нигде не сохраняется, решение владельца).
# Настройка netrc (один раз, в своём терминале):
#   mkdir -p ~/.config/keenetic && chmod 700 ~/.config/keenetic
#   read -rsp 'Pass admin@192.168.1.1: ' P; echo
#   printf 'machine 192.168.1.1\nlogin admin\npassword %s\n' "$P" > ~/.config/keenetic/api.netrc
#   unset P; chmod 600 ~/.config/keenetic/api.netrc
# Использование:
#   scripts/rci.sh show/version          # GET-путь = CLI-команда через /
#   scripts/rci.sh "show system"         # аргумент можно с пробелами
set -euo pipefail

HOST="${KEENETIC_HOST:-192.168.1.1}"
USER="${KEENETIC_USER:-admin}"
NETRC="${KEENETIC_NETRC:-$HOME/.config/keenetic/api.netrc}"

command -v curl >/dev/null || { echo "нужен curl" >&2; exit 1; }

if [[ -f "$NETRC" ]]; then
  # пароль берётся из netrc-файла самим curl
  curl -sfS --netrc-file "$NETRC" "http://${HOST}/rci/$1"
else
  read -rsp "Пароль ${USER}@${HOST}: " PASS; echo
  curl -sfS -u "${USER}:${PASS}" "http://${HOST}/rci/$1"
fi
echo
