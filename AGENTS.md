# Домашняя сеть: Keenetic Ultra (KN-1811)

Репозиторий для управления домашней сетью и роутером Keenetic Ultra (KN-1811).
Этот файл — память для агента: основные принципы работы с роутером и правила безопасности.

## Железо и топология

- Роутер: **Keenetic Ultra (KN-1811)**, IP `192.168.1.1`, **KeeneticOS 5.x**
- Архитектура CPU: **aarch64** → пакеты Entware/OPKG — ветка `aarch64-k3.10`
- Mesh: Ultra — главный узел Wi-Fi-системы, ещё 2 узла Keenetric (слабее модели уточняются).
  Настройки Wi-Fi/mesh не трогать без явной задачи — сломается покрытие всего дома.
- Управляющий Mac в сети 192.168.1.0/24 (провод/Wi-Fi, en0).

## Цели (скоуп репозитория)

1. **VPN через VLESS**: XKeen 2.0 (форк JamesZero) на роутере, режим **Hybrid** — основной способ
   обхода блокировок и сплита трафика. Ядро: **Mihomo — основное**, Xray — запасное
   (переключение `xkeen -mihomo` / `xkeen -xray`). Роутинг — whitelist (см. «Решения»).
2. **Сетевое хранилище**: SMB-шара на USB-диске.
3. **Торрент-клиент**: Transmission в Entware.
4. Прошивка/обновление KeeneticOS, управление компонентами OPKG, тонкие кастомизации, доступ по SSH.

## Решения (что делаем)

- **2026-11-01: Смена KZ-ноды cactus-kz → cactus-vk-kz (Reality, сервер на Xray-core 26.6.27).**
  Ссылка с fp=firefox в mihomo не работает («REALITY authentication failed»): XTLS с лета 2026
  требует в ClientHello пост-квантовую группу X25519MLKEM768 (с v26.7.11 — официальная граница
  несовместимости с mihomo, с v26.9.08 — жёсткий разрыв), а mihomo по умолчанию эту группу
  вырезает и чинить не будет (MetaCubeX/mihomo#3193, closed not planned). Рабочее решение
  (проверено живьём): `client-fingerprint: chrome` + `reality-opts.support-x25519mlkem768: true`
  — опция mihomo-специфичная, в vless://-ссылках не передаётся, вписывается руками; firefox-fp
  в mihomo бесполезен (HelloFirefox_120 без ML-KEM, utls v1.8.7). Промежуточно ставили WS-ссылку
  (работала), по решению владельца убрали — итог: Reality+vision. Имя outbound `reality-kz`
  сохранено (группы AI/VK/YouTube/Meta/Google не менялись). Проверено после hot-reload
  (PUT /configs): delay 128–131 мс, AI=128, egress 176.123.179.193 (loc=KZ), reality-home (NL)
  не задет (69–78 мс), правила/kz-pool на месте. Бэкапы: `backups/20261101-kz-node-replace/`
  (исходный + WS-вариант), на роутере `config.yaml.bak-20261101` и `config.yaml.bak-20261101-ws`.
  Если сервер обновят до 26.9.8+ — текущая связка продолжит работать (проверено сообществом);
  полное расследование с таймлайном и матрицей тестов: `xray-problem.md`.
- **2026-11-01: Kimi (kimi.ai) — напрямую, без VPN.** Исключение из AI-пула:
  `DOMAIN-SUFFIX,kimi.ai,DIRECT` первой строкой после QUIC REJECT, выше kz-pool
  и category-ai. Только kimi.ai с поддоменами; API-платформа moonshot.ai
  (api/platform) остаётся через KZ, kimi.com/moonshot.cn и так DIRECT.
  Проверено живьём: kimi.ai/www.kimi.ai → DIRECT, Claude/ChatGPT/moonshot
  по-прежнему AI → reality-kz. Бэкап: `backups/20261101-kimi-direct/`.
- **2026-11-01: `cloud.vk.kz` (VK Cloud KZ) — через KZ с fallback на прямое соединение.**
  Отдельная группа `VK` (type: fallback): `[reality-kz, DIRECT]` — KZ недоступна
  → напрямую через провайдера (РФ). Правило `DOMAIN-SUFFIX,cloud.vk.kz,VK` стоит
  до adlist/refilter. Сами `vk.kz` адресов не имеет (NXDOMAIN A), vk.com не
  трогаем — владелец попросил строго cloud.vk.kz. Естественный failover ~3 мин
  (interval 60 × max-failed-times 3); мгновенно — latency-тестом группы в zashboard.
  Проверено живьём: KZ-маршрут (HTTP 200), принудительный отказ → DIRECT (HTTP 200),
  возврат на KZ. Бэкап: `backups/20261101-vk-kz/`.
- **2026-10-30, 21:19 МСК: Google, YouTube и Meta также переведены на KZ для пробы.**
  Владелец согласовал целые группы (включая Facebook и прочие Google-домены).
  В трёх select-группах выбран reality-kz, он же первый вариант в конфиге;
  прежние ручные варианты сохранены. Google-правило поднято выше refilter,
  иначе google.com продолжал идти через основной NL-пул. Живые TLS/цепочки
  Google/YouTube/ytimg/Instagram/Facebook проверены: KZ. AI по-прежнему KZ-only,
  Fallback/Fastest для остальных сервисов — NL. Подробнее: `docs/kz-google-meta.md`.
  Это более новое решение, чем сохранение YouTube/Meta на NL в записи ниже.
- **2026-10-30: AI/платежи/верификация — KZ-only, спека 003 (заменяет US-схему 002).**
  `AI = [reality-kz]`, единственный VLESS+Reality выход Казахстан, без fallback,
  DIRECT и ручных NL-альтернатив. Весь `category-ai` + `mihomo/kz-pool.list`
  (Anthropic/Claude, Stripe/Link/hCaptcha, Persona, Yoti, точные intake-хосты
  Claude Code). Persona — личность/бизнес; Yoti — возраст. KZ упала → этот
  трафик падает; это относится ко всему Stripe/hCaptcha в LAN, не только Claude.
  Порядок QUIC REJECT → kz-pool AI → category-ai AI → adlist REJECT.
  YouTube/Meta/остальной основной пул сохраняют NL, `Fallback=[reality-home,DIRECT]`;
  KZ исключён из Fastest и всех остальных сервисных групп. US удалён из рабочего
  Mihomo, `us-pool.list` — исторический снимок. Владелец сам выключает US-VM.
  Выход 89.126.205.135/KZ/Almaty проверен; отказ KZ и восстановление проверены живьём.
  **Граница, согласованная владельцем:** только текущий веб-перехват 80/443;
  это не общий kill-switch (ECH/неизвестные домены/STUN/другие порты не покрыты).
  Общие Google OAuth/Maps/Fonts и CDN библиотек владелец оставил на прежних маршрутах.
  Запасной Xray НЕ поддерживает KZ-only: не переключать на него как восстановление AI.
  Список → копия `/opt/etc/mihomo/kz-pool.list` → reload `kz-pool@classical`.
  Спека/источники/приёмка: `docs/specs/003-kz-ai-routing/`; ADR: `docs/adr/001-kz-only-ai.md`.
- **2026-10-30: Anthropic/Persona в US-пуле.** В `mihomo/us-pool.list` добавлены
  `withpersona.com` со всеми поддоменами, домены Anthropic/Claude из v2fly и точный
  CDN `servd-anthropic-website.b-cdn.net`. Persona — партнёр проверки личности
  Anthropic; `persona.com` и ошибочное `whispersona.com` не используются.
  Hot-reload применён, живое `inquiry.withpersona.com` подтверждено через
  `us-pool@classical → AI → US-Fallback → reality-us`.
  Подробности: `docs/specs/002-us-ai-routing/anthropic-persona.md`.
- **2026-10-15: US-нода для AI-трафика (сплит US/NL), спека 002.** Второй прокси
  `reality-us` (VLESS+Reality, US/EWR) в Mihomo; вся группа AI (`category-ai` +
  file-провайдер `us-pool.list`) идёт через `US-Fallback = [reality-us, reality-home]`
  БЕЗ DIRECT — US упала → AI на NL (~минута), обе ноды вниз → AI падает (осознанно:
  для AI DIRECT бессмыслен). Основной пул (YouTube, Meta, прочий whitelist) НЕ менялся:
  `Fallback = [reality-home, DIRECT]`. Список US-доменов вне AI-категории —
  `mihomo/us-pool.list` в репо (источник истины): правка → scp/vi на роутер →
  reload в zashboard (Rule Providers), без рестарта ядра. На запасном ядре Xray
  сплита НЕТ — при `xkeen -xray` весь AI идёт через NL, US-only сервисы не работают.
  Спека и хроника: `docs/specs/002-us-ai-routing/`. Внедрено и принято 2026-10-15
  (failover US→NL→US проверен живьём, hot-reload проверен).
- **2026-10-01: QUIC (UDP/443) через VPN НЕ прокидываем — ограничение стека.** Гипотеза
  «пустить QUIC Meta/YouTube через прокси» проверена и опровергнута: xray-core на
  Reality-инбаундах молча дропает UDP-сессии на порт 443 (доказано управляемым
  эхо-тестом на обоих хопах RU→NL: udp:9443 через тот же туннель возвращается,
  udp:443 — нет; plaintext VLESS без Reality релеит оба). Телефон при этом ловил
  тихий таймаут вместо быстрого отказа — хуже, чем REJECT. Глобальное правило
  `quic@inline → REJECT` в Mihomo — осознанно правильное, оставлено. Откат
  эксперимента: конфиг восстановлен из бэкапа `backups/20261001-quic-meta/` (md5
  сверен). Диагноз редких подлагиваний reels: инфраструктура чиста (7 дней журнала
  xray без ошибок, delay 58 мс, цепочка 45–110 Мбит/с вечером против 154 днём);
  вероятные причины — Wi-Fi/mesh телефона и вечерняя загрузка плеча дом→RU.
- **2026-09-19: VPN-стек = XKeen 2.0 + ядро Mihomo (основное), Xray — запасное.**
  Режим Hybrid (порт 443 не переносим). Роутинг — whitelist: динамические rule-sets
  (zxc-rv `.mrs` / legiz-ru / Re:filter, автообновление раз в сутки: YouTube, Meta/Instagram,
  Telegram, Discord и т.п.) + собственные строки `DOMAIN-SUFFIX` в конфиге Mihomo.
  Финальное правило `MATCH,DIRECT` — всё вне списков идёт напрямую. ВНИМАНИЕ (2026-09-20):
  в XKeen 2.0 пустой `/opt/etc/xkeen/port_proxying.lst` означает перехват ВСЕХ портов!
  Явно прописаны `80` и `443` (TCP+UDP) — только веб-трафик идёт через ядро; игровой и
  прочий UDP ходит напрямую мимо прокси; при проблемах — игровой ПК вне политики
  `xkeen` (нулевое вмешательство). DNS клиентов не
  переопределяем (домены определяет sniffer по SNI); в Keenetic включить нативные DoT/DoH.
  sing-box/SKeen не используем (решение 2026-09-19: те же возможности, но ручная сборка).
  В репо — только `*.template.*`; реальный config.yaml с UUID/ключами Reality — только на роутере.

## НЕ делаем (решения владельца)

- **RCI API (HTTP `/rci/`) не используется** (решение владельца, 2026-09-19): подход не
  заработал (401 при авторизации). Управление роутером — только через веб-интерфейс и
  SSH/CLI. Не предлагать curl к `/rci/`, netrc-креды и MCP-обёртки над RCI (keenetic-mcp и т.п.).
- **usbipd-win не используется** (решение владельца, 2026-09-19). Причина: канал USB/IP
  через WSL2 нестабилен — постоянные обрывы соединения под нагрузкой (I/O errors,
  «connection closed», устройство пропадает во время операций). Из-за этого badblocks
  выдал ложный вердикт «98% битых блоков» на исправной флешке (прямая проверка DiskGenius
  на Windows: все сектора good). Работу с USB-носителями делать: форматирование/проверка —
  DiskGenius в Windows (умеет ext4), файлы на ext4-диск — через SMB-шару роутера.

## Доступ к роутеру

| Канал | Как |
|---|---|
| Веб-интерфейс | http://192.168.1.1 (порты 80/443) |
| SSH (Keenetic) | **Закрыт** — компонент «Сервер SSH» не установлен |
| SSH (Entware) | **Работает** (проверено 2026-09-19): `ssh -i .ssh/keenetic-agent-2026-09-19 root@192.168.1.1` (порт 22, dropbear). Ключ агента — `.ssh/keenetic-agent-2026-09-19` (в gitignore). Публичные ключи на роутере лежат в `/opt/etc/dropbear/authorized_keys` (НЕ в `~/.ssh/`) |

**Креды (логин/пароль) НИКОГДА не хранятся в репозитории и файлах репо.** Только интерактивный
ввод в момент работы (допустима macOS Keychain). Конфиги с секретами (UUID VLESS, ключи REALITY,
пароли) в git не коммитить — только шаблоны `*.template.*` с плейсхолдерами.

## Правила безопасности (критично)

1. **Running-config ≠ сохранённый конфиг — но только для CLI.** Изменения через
   **веб-интерфейс KeeneticOS сохраняет автоматически**; изменения через **CLI
   (telnet/ssh-консоль Keenetic)** живут до перезагрузки — нужен `system configuration save`.
   Цикл любой правки: проверить → спросить владельца → применить → убедиться, что работает;
   для CLI-правок — ещё и save. Сущности вне NDM-конфига (Entware в /opt, XKeen, его файлы
   и iptables-правила) переживают перезагрузку через скрипты автозагрузки Entware — к save
   отношения не имеют.
2. **Бэкап перед изменениями**: CLI `more running-config` или веб (Управление → Конфигурация).
   Сохранять в `backups/` (в .gitignore).
3. **Не резать сук**: не отключать/перенастраивать интерфейсы и Wi-Fi, через которые идёт текущий
   доступ (в т.ч. mesh-backhaul) — потеряем управление роутером.
4. **Порт 443 занят веб-интерфейсом.** Режим TProxy в XKeen требует освободить 443; режим
   **Hybrid (Mixed) — не требует**. По умолчанию планировать Hybrid.
5. **Роутер — прод.** Эксперименты — после бэкапа и с планом отката (`xkeen -remove`,
   отключение OPKG, откат компонентOS).
6. Обновления KeeneticOS ставить осознанно: сначала проверить совместимость XKeen/Entware с новой веткой OS.

## Инструментарий

- XKeen — форк **JamesZero 2.0** (доки сообщества: Corvus-Malus/XKeen) — единственная ветка
  с поддержкой KeeneticOS 5+. Оригинал Skrill0/XKeen устарел.
- Шаблон Mihomo под XKeen: https://github.com/zxc-rv/assets/blob/main/config_templates/mihomo/config.yaml
  (группы сервисов, sniffer, панель zashboard). Rule-sets: zxc-rv `.mrs` (auto 24 ч),
  https://github.com/legiz-ru/mihomo-rule-sets, Re:filter https://github.com/1andrevich/Re-filter-lists.
  Генератор outbound-блока из vless://-ссылки: https://zxc-rv.github.io/XKeen-UI/Outbound_Generator/
- Ссылки на официальные доки и проверенные репо: `docs/sources.md`.
- Инструкция внедрения/переустановки VPN (чек-лист + план автоматизации): `docs/deploy-vpn.md`.

## Конвенции репозитория

- **Spec Kit в этом репозитории не применяем** (решение владельца 2026-10-30, подтверждено 2026-11-01):
  без спек-гейтов, reviewer-итераций и мутационных ревью; существующие `docs/specs/`
  остаются как архив истории. После изменений — ручная проверка на живом роутере.
- **Тесты — только минимальные и мгновенные** (локальный unittest по контракту
  конфига, ~0.01 с, `python3 -m unittest discover -s mihomo -p 'test_*.py'`);
  TDD-процесс и обязательные ревью тестов не используем.
- Документация на русском; в скриптах краткие русские комментарии.
- Bash: `set -euo pipefail`, никаких секретов в коде.
- Новые знания о роутере (версия OS, компоненты, диски, устройства mesh) — фиксировать в `docs/router.md`.
- Значимые решения (что делаем/что нет) — дописывать в этот файл с датой.
