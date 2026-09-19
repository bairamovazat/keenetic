# План: XKeen (Xray) + VLESS на Keenetic Ultra KN-1811

Основной VPN и сплит трафика: управление — пользовательские политики Keenetic +
IPSET/geosite поверх основной сети.

## Вводные и решения

| Вопрос | Решение |
|---|---|
| Ветка XKeen | **Форк JamesZero 2.0** (инструкция Corvus-Malus) — только он поддерживает KeeneticOS 5+ |
| Ядро | Xray (VLESS), альтернатива — Mihomo (`-mihomo`) |
| Режим | **Hybrid (Mixed)** по умолчанию: не требует освобождать 443 (занят веб-интерфейсом). TProxy — опционально позже, с переносом веб-морды |
| Сплит | Пользовательские политики Keenetic (какие устройства через прокси) + ipset/geosite (какие домены/IP) |
| Геобазы | zkeen.dat/zkeenip.dat или Re:filter, обновление по cron (`xkeen -ug`) |

## Этапы

### 0. Подготовка (до кода)
- [ ] Получить от владельца: vless://-ссылку от VPN-провайдера (uuid, адрес, publicKey, SNI, shortId).
- [ ] Бэкап running-config → `backups/`.

### 1. KeeneticOS: компоненты (веб → Управление → Общие настройки → Изменить набор компонентов)
- Интерфейс USB, Файловая система Ext, Общий доступ к файлам по SMB (нужен и для хранилища),
  **Поддержка открытых пакетов (OPKG)**, Модули ядра Netfilter, Прокси DoT/DoH.
- ❌ «Сервер SSH» НЕ ставить — SSH даст Entware (иначе конфликт портов; см. AGENTS.md).

### 2. USB-накопитель
- Разметка: **SWAP 512M–1G первым разделом** + EXT4 «OPKG» остальное. ФС строго EXT4.
- С macOS: `diskutil partitionDisk` + `mkfs.ext4 -O ^metadata_csum` (e2fsprogs из brew)
  или скрипт keenetic-entware-flash. Ссылки в docs/sources.md.

### 3. Entware (aarch64)
- `aarch64-installer.tar.gz` (KN-1811 → ветка aarch64-k3.10) → на диск в папку `install/`
- Веб → OPKG: выбрать диск, initrc оставить пустым → перезагрузка → установка из системного журнала
- SSH Entware: `root@192.168.1.1:22`, дефолт-пароль `keenetic` → сразу `passwd`.
- `opkg update && opkg upgrade`.

### 4. XKeen
```sh
# на роутере (ssh Entware)
opkg install curl ca-certificates
curl -o /tmp/xkeen https://raw.githubusercontent.com/.../xkeen   # ссылка из инструкции Corvus-Malus
chmod +x /tmp/xkeen && /tmp/xkeen -i    # интерактивно: ядро Xray, режим Hybrid, автозапуск on
```

### 5. Конфиг Xray (VLESS)
- Шаблон `xray/config.template.json` в этом репо (плейсхолдеры), реальный конфиг на роутере:
  `/opt/etc/xray/config.json` (секреты в git не попадают).
- Outbound: VLESS + REALITY (uuid, publicKey, shortIds, serverName), flow: xtls-rprx-vision.
- Проверка синтаксиса: `xkeen -xtest`. Логи: `xkeen -log`.

### 6. Сплит трафика
- Кому через прокси: пользовательские политики Keenetic (веб → Приоритеты подключений) + привязка
  устройств к политике; XKeen 2.0 умеет работать с пользовательскими политиками (wiki/Configuration).
- Что через прокси: IPSET-режим XKeen + geosite (ру-сегменты и крупные блок-листы), исключения —
  `ip_exclude.lst`, порты — `port_proxying.lst` / `port_exclude.lst` в /opt/etc/xkeen/.
- DNS: зашифровать (DoT/DoH keenetic; опционально `xkeen -dns`), чтобы не было DNS-утечек.

### 7. Проверка перед сохранением
- С устройства из политики: внешний IP ≠ домашний, целевые сайты открываются.
- Без прокси (прямая политика): ру-сайты напрямую, скорость не просела.
- `system configuration save` — только после подтверждения владельцем.

### 8. Эксплуатация
- Обновление гео: `xkeen -ug` (+ cron `xkeen -ugc`).
- Обновление Xray: `xkeen -ux`. Откат всего: `xkeen -remove` + бэкап конфига.

## Известные грабли (из инструкции сообщества)

- Режим TProxy требует 443 на роутере — у нас занят веб-интерфейсом → пока Hybrid.
- KeeneticOS 5+: компонент IPv6 всегда включён; XKeen 2.0 умеет управлять (`-ipv6`).
- После Entware не ставить встроенный «Сервер SSH» (конфликт).
- Автозапуск XKeen в своём политическом контуре (FAQ п.12 форка) — не «на всё устройство».
