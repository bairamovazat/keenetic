#!/usr/bin/env bash
# scripts/rci.sh — обёртка над RCI API Keenetic (192.168.1.1).
# Пароль вводится интерактивно и нигде не сохраняется (решение владельца).
# Использование:
#   scripts/rci.sh show/version          # GET-путь = CLI-команда через /
#   scripts/rci.sh "show system"         # аргумент можно с пробелами
set -euo pipefail

HOST="${KEENETIC_HOST:-192.168.1.1}"
USER="${KEENETIC_USER:-admin}"

command -v curl >/dev/null || { echo "нужен curl" >&2; exit 1; }

read -rsp "Пароль ${USER}@${HOST}: " PASS; echo

# GET /rci/<путь/команды>; без авторизации роутер вернёт 401
curl -sfS -u "${USER}:${PASS}" "http://${HOST}/rci/$1"
echo
