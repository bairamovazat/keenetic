# Торренты: Transmission на KN-1811

## Статус (2026-09-19)

Развёрнут **встроенный Transmission KeeneticOS** («Загрузка и качание», через веб-UI,
не Entware). Порт RPC 8090, данные: `/tmp/mnt/1b83a805-.../download` (раздел Media на SSD).

**Авторизация — навязывается KeeneticOS, settings.json тут не главный:**
- `http://192.168.1.1/app/transmission/web/` (порт 80, прокси ОС) — логин пользователя KeeneticOS;
- `http://192.168.1.1:8090/transmission/web/` — basic-auth учёткой пользователя KeeneticOS
  с правом **«Доступ к управлению закачками»** (Управление → Пользователи и доступ).
Правки rpc-auth/rpc-password в settings.json ОС игнорирует. Если 8090 не пускает —
проверить галочку у пользователя, раскладку, кеш браузера (приватное окно).

Entware-Transmission НЕ устанавливать — два демона одновременно нельзя.
Ручная правка settings.json: выключить тумблер в вебе → править файл → включить тумблер
(иначе демон перезапишет конфиг). `watch-dir` — папка автодобавления: положил .torrent →
качается (удобно для своего будущего приложения).

## Выбор клиента

| Клиент | RAM | UI | RPC/API | Вердикт |
|---|---|---|---|---|
| **Transmission (Entware)** | ~20–50 МБ | скромный (transmission-web) | JSON-RPC 9091 — идеален под своё приложение | **наш выбор** |
| qBittorrent-nox (Entware) | 80–200+ МБ | красивый, поиск, категории | WebUI API v2 | запасной: на 512 МБ RAM впритык вместе с Xray |
| Встроенный «Загрузка и качание» (KeeneticOS) | под контролем ОС | веб Keenetic | ограниченный | НЕ ставить одновременно с Entware-Transmission |
| rTorrent/ruTorrent | средняя | устаревший | — | пропускаем |

Решающий аргумент: RAM всего 512 МБ (ОС + будущий Xray), а под кастомное приложение
нужен чистый JSON-RPC — Transmission даёт и то, и другое.

## Установка (в SSH-сессии на роутере)

```sh
opkg update
opkg install transmission-daemon transmission-web transmission-remote
mkdir -p /tmp/mnt/Media/downloads /tmp/mnt/Media/movies /tmp/mnt/Media/series
```

## Настройка

1. Остановить демон (если стартовал сам): `/opt/etc/init.d/S88transmission stop`
   (имя скрипта сверить: `ls /opt/etc/init.d/`)
2. Найти settings.json (показывает init-скрипт): `grep -i config /opt/etc/init.d/S88*`
3. Ключевые поля settings.json:
   - `"download-dir": "/tmp/mnt/Media/downloads"`
   - `"rpc-bind-address": "0.0.0.0"`, `"rpc-port": 9091`,
     `"rpc-authentication-required": true`, `"rpc-username"`, `"rpc-password"`
   - `"peer-limit-global": 150`, `"peer-limit-per-torrent": 30` (экономия RAM)
   - `"umask": 2` (чтобы файлы были доступны по SMB всем)
   - `"dht": true`, `"speed-limit-down-enabled": false`
4. Запуск: `/opt/etc/init.d/S88transmission start`
5. Веб-морда: http://192.168.1.1:9091 (только из LAN — наружу не пробрасывать)

## Автостарт

Entware init-скрипты (S88…) запускаются автоматически при старте OPKG — отдельно
прописывать не нужно. Проверка после перезагрузки роутера: `ps | grep transmission`.

## Политика интернета (важно с XKeen)

Когда появится XKeen: torrents должны ходить НАПРЯМОМУ, не через прокси —
веб → Приложения → Transmission → «Политика доступа» → Напрямую
(или CLI-политикой, ст. 50384 в docs/sources.md).

## Просмотр с устройств

- iOS: **Infuse** (или VidHub) → источник SMB `\\192.168.1.1\Media` → библиотека
  с постерами, позиции просмотра синхронизируются через iCloud, новые серии подтягиваются сами.
- Windows: сетевой диск `\\192.168.1.1\Media` + PotPlayer/VLC.
- Структура каталогов (важно для сканеров метаданных):
  `movies/Название (Год)/`, `series/Шоу/S01/Шоу S01E01.mkv`; добавление торрентов —
  веб-морда Transmission из любого устройства.
- Будущее: Jellyfin-сервер на N100-NAS (server-side resume на все устройства,
  Infuse как клиент); на роутере Jellyfin не поднимать — RAM. Своё мини-приложение
  (сортировка downloads → библиотека, своя логика) — после переезда на NAS.
- DLNA (встроенная «Медиатека»): включить как канал для ТВ/приставок (компонент
  «Медиатека DLNA» → раздел Media). Без позиций просмотра и метаданных — это дополнение
  к Infuse, не замена. Индексирует весь раздел, включая downloads.

## Бэкап ценного

`/opt/etc/transmission*/settings.json` + список торрентов (`/opt/var/transmission/...` —
сверить путь) — в бэкап слоя 3 (см. entware-opkg.md).
