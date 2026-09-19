# Источники и инструменты

Проверенные ссылки. Порядок: официальное → XKeen → агентские инструменты → сообщество.

## Официальные (Keenetic)

- help.keenetic.com — база знаний (установка OPKG, SMB, компоненты, Wi-Fi System)
- support.keenetic.ru/eaeu/ultra/kn-1811/ru/ — статьи по конкретно KN-1811
  (пример: подготовка USB-диска как хранилища и SWAP)
- docs.keenetic.com — веб-документация интерфейса
- keenetic.com — продуктовые страницы (защита от ботов: парсится плохо, лучше браузер)
- RCI API: JSON-зеркало CLI-дерева поверх HTTP (`/rci/...`). Публичной полной доки нет —
  практичная шпаргалка: https://github.com/salatmaster/keenetic-mcp/blob/main/docs/rci-api.md

## VPN: XKeen / Xray / VLESS

- **https://github.com/Corvus-Malus/XKeen** — инструкция сообщества (для быстрой настройки).
  ОСНОВНОЙ ИСТОЧНИК для нас: описывает форк XKeen 2.0 с поддержкой KeeneticOS 5+.
- https://github.com/jameszeroX/XKeen — сам форк 2.0 (от 06.2026) + wiki/Configuration
  (режимы TProxy/Hybrid, пользовательские политики, IPSET, DNS, параметры запуска).
- https://github.com/Skrill0/XKeen — оригинальный XKeen (не обновляется с 2024, до OS 4 — не наш вариант).
- https://github.com/zxc-rv/XKeen-UI — веб-панель управления XKeen (опционально).
- Гео-базы: https://github.com/jameszeroX/zkeen-domains (zkeen.dat), https://github.com/jameszeroX/zkeen-ip (zkeenip.dat), альтернатива Re:filter https://github.com/1andrevich/Re-filter-lists
- Генератор конфигов: https://github.com/Corvus-Malus/XKeen-Config-Generator

## Агентский доступ / автоматизация

- **https://github.com/salatmaster/keenetic-mcp** — MCP-сервер поверх RCI API + 4 скилла
  (keenetic-rci, keenetic-safe-changes, keenetic-segments, keenetic-troubleshoot).
  Проверен на Ultra KN-1811 / KeeneticOS 5.1.3. Ничего не ставит на роутер; пароль — в macOS Keychain;
  изменения не сохраняются без явного `save_config`. Запуск: `npx -y keenetic-mcp`.

## Entware / OPKG

- **Официальная инструкция (пошагово, проверена 2026-09-19)**: https://support.netcraze.ru/hero-5g/nc-4110/ru/20980-installing-the-entware-repository-on-a-usb-drive.html
  (netcraze.ru = новый бренд Keenetic; статья «Установка репозитория Entware на USB-накопитель»).
  Порядок: диск в EXT4 → компонент ОС «Поддержка открытых пакетов» (OPKG) → диск в роутер →
  в корень раздела папка `install/` с `aarch64-installer.tar.gz` (для KN-1811) →
  веб: «Менеджер пакетов OPKG» → выбрать накопитель + «Доступ для учетной записи пользователя» →
  Сохранить (установка идёт автоматически, лог — в Системном журнале).
  После установки: SSH `root@192.168.1.1`, пароль `keenetic`, порт **222** если установлен
  компонент «Сервер SSH», иначе **22**; сразу `passwd` и `opkg update`.
  Техподдержка Entware не консультирует — форум: forum.keenetic.com, раздел «Открытые пакеты OPKG».
- Производительность Transmission (ext4 без преаллокации, swap, лимиты): https://support.netcraze.ru/hero-5g/nc-4110/ru/43341-maximising-the-performance-of-the-download-station.html
- ext4 на USB (компонент «Файловая система Ext», форматирование, tune2fs -m 0): https://support.netcraze.ru/hero-5g/nc-4110/ru/21024-using-the-ext4-file-system-on-usb-drives.html
- Политика доступа Transmission (напрямую/через VPN): https://support.netcraze.ru/hero-5g/nc-4110/ru/50384-how-to-change-an-internet-connection-policy-for-download-station-.html
- Пакеты: https://bin.entware.net/aarch64-k3.10/ (ветка для KN-1811; там же keenetic/-список)
- Установщик: https://bin.entware.net/aarch64-k3.10/installer/aarch64-installer.tar.gz
- Подготовка флешки с macOS: https://github.com/MaxXxaM/keenetic-entware-flash
  (одной командой SWAP+EXT4) или вручную diskutil + e2fsprogs (mkfs.ext4 `-O ^metadata_csum`).

## Форумы / сообщество (информация и характеристики)

- **4PDA, тред Ultra/Titan KN-1811**: https://4pda.to/forum/index.php?showtopic=1065475
  (~515 страниц). Шапка = полные характеристики железа, обзоры, прошивки, сборник ссылок.
  NB: 4PDA отдаёт страницы в **cp1251** — при парсинге: `curl ... | iconv -f cp1251 -t utf-8`;
  без логина часть форума недоступна.
- Справочник команд CLI по KN-1811 (официальный PDF):
  https://storage.googleapis.com/docs.help.keenetic.com/cli/4.0/ru/cli_manual_kn-1811_ru.pdf
  (шаблон пути: `docs.help.keenetic.com/cli/<версия>/ru/cli_manual_kn-1811_ru.pdf`)
- 4PDA, главный тред Entware на Keenetic (NDMS V2 + Entware):
  https://4pda.to/forum/index.php?showtopic=535079
- keeneticservice.ru — официальный FAQ по сервисам Keenetic

## Сообщество: инструменты (альтернативы/дополнения, оценивать отдельно)

- https://github.com/nfqws/nfqws-keenetic, /nfqws2-keenetic — anti-DPI (обход замедления без VPN)
- https://github.com/Ground-Zerro/HydraRoute — доменная маршрутизация в VPN для Keenetic
- https://github.com/spatiumstas/web4static — веб-панель над многими инструментами (XKeen, NFQWS, …)
- https://github.com/rekryt/iplist — списки IP в форматах в т.ч. keenetic
- Форум: https://forum.keenetic.com (тред установки Entware, тред XKeen)
