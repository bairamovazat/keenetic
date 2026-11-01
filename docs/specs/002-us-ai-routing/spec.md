# Спека 002: AI-трафик через US-ноду (сплит US/NL)

Дата: 2026-10-15. Статус: ВНЕДРЕНО И ПРИНЯТО 2026-10-15 (приёмка — см. review-log.md).

## Контекст

Сейчас единственный прокси `reality-home` (VLESS+Reality, RU→NL) обслуживает весь
whitelist (mihomo/config.yaml.template:49). Весь AI-трафик идёт через NL по правилу
`RULE-SET,category-ai@domain,AI` (строка 205). Владелец добавляет вторую ноду
Reality в США (Нью-Йорк): ChatGPT/Codex и Claude Code требуют US-выхода, при этом
трафикоёмкие YouTube/Instagram должны остаться на NL.

## Цель

1. Новый прокси `reality-us` (VLESS+Reality, US) в конфиге Mihomo.
2. Весь AI-пул (`category-ai@domain`) — через US с fallback на NL.
3. Расширяемый список US-доменов вне AI-категории — отдельным файлом в репо
   (us-pool.list), правка без рестарта ядра (hot-reload из zashboard).
4. Основной пул (YouTube, Meta, прочий whitelist) — без изменений: NL → DIRECT.

## Решения владельца (2026-10-15, ответы на вопросы спеки)

1. **Состав US-пула**: весь `category-ai@domain` (не точечный список) — ChatGPT,
   Claude, Gemini, Mistral, Perplexity и др. уезжают на US. Осознанно.
2. **Fallback US-пула**: US → NL, БЕЗ DIRECT. Обе ноды недоступны → AI-трафик
   падает (для AI DIRECT бессмыслен — RU-IP блокируются сервисами).
3. **Хранение списка**: отдельный file-провайдер `us-pool.list`; репо — источник
   истины, на роутере — рабочая копия; добавление домена = строка + reload из панели.
4. **Основной пул не трогаем**: `Fallback = [reality-home, DIRECT]` (fail-open,
   решение 2026-09-19) — US-нода не участвует в основном fallback.

## Изменения конфигурации

Файл `mihomo/config.yaml.template` (зеркально на роутер в `/opt/etc/mihomo/config.yaml`):

1. **proxies** — добавить после `reality-home`:
   ```yaml
   - name: reality-us
     type: vless
     server: <US_HOST>
     port: 443
     udp: true
     uuid: <US_UUID>
     flow: xtls-rprx-vision
     tls: true
     servername: <US_SNI>
     client-fingerprint: chrome
     reality-opts:
       public-key: <US_PBK>
       short-id: <US_SID>
   ```
   Параметры — из vless://-ссылки владельца (блок outbounds соберёт генератор
   zxc-rv; spx в mihomo не используется — как у reality-home).
   Проверить при заполнении: ссылка US-ноды должна быть `flow=xtls-rprx-vision`
   + `fp=chrome` (зеркало reality-home); при отличиях — скорректировать поля.
2. **proxy-groups** — добавить скрытую группу:
   ```yaml
   - name: US-Fallback
     type: fallback
     url: https://www.gstatic.com/generate_204
     interval: 60
     max-failed-times: 3
     hidden: true
     proxies: [reality-us, reality-home] # US упала (3 провала) → NL; DIRECT нет (решение 2)
   ```
   include-all НЕ использовать: он допишет DIRECT (и прочие прокси) в КОНЕЦ
   списка → после падения обеих нод fallback молча уйдёт в DIRECT (fail-open),
   что запрещено решением 2. Механика include-all («дописывает после явного
   списка», parser.go) подтверждена исходниками mihomo — итерация 1.
3. **Группа AI** — дефолт на US-цепочку, ручные опции сохранить:
   ```yaml
   proxies: [US-Fallback, Заблок. сервисы, Fallback, Fastest, DIRECT]
   ```
   `profile.store-selected` включён (проверено итерацией 5 спеки 001) — ручной
   выбор в zashboard переживает рестарт.
4. **rule-providers** — добавить file-провайдер:
   ```yaml
   us-pool@classical:
     type: file
     behavior: classical
     format: text
     path: us-pool.list        # относительно каталога конфига: /opt/etc/mihomo/
   ```
5. **rules** — перед `RULE-SET,category-ai@domain,AI` (строка 205) добавить:
   ```yaml
   - RULE-SET,us-pool@classical,AI   # свои US-домены вне AI-категории
   ```
   Цель — группа AI (не US-Fallback напрямую): переключение AI-группы в панели
   управляет обоими правилами одной кнопкой.
6. **Новый файл** `mihomo/us-pool.list` в репо (НЕ шаблон — домены не секрет,
   коммитится как есть). Начальное содержимое — плейсхолдер:
   ```
   # US-пул: домены, которые идут через US-ноду вне category-ai.
   # Репо — источник истины; после правки синхронизировать с роутером.
   DOMAIN-SUFFIX,example.invalid
   ```
7. **Воркфлоу правки us-pool.list** (панель умеет только перечитать файл,
   не редактировать):
   (а) изменить `mihomo/us-pool.list` в репо (коммит);
   (б) перенести на роутер: `scp mihomo/us-pool.list root@192.168.1.1:/opt/etc/mihomo/`
       (или vi/nano по SSH Entware);
   (в) zashboard → Rule Providers → us-pool@classical → «обновить» (hot-reload,
       без рестарта ядра).
8. **Шапка-комментарий шаблона** — дополнить списком изменений 002 и поправить
   обоснование отказа от include-all у основного Fallback (см. изменение 2:
   include-all дописывает прокси ПОСЛЕ явного списка — для [reality-home, DIRECT]
   это дало бы выбор DIRECT раньше добавленных нод; формулировка «DIRECT первым
   кандидатом» неточна).

## Что НЕ меняется

- `Fallback = [reality-home, DIRECT]`, все сервисные группы и их дефолты
  (кроме группы AI — её дефолт меняется на US-Fallback, изменение 3).
- QUIC REJECT (UDP 443) — остаётся; web-клиенты AI откатываются на TCP, как сейчас.
- `MATCH,DIRECT`, порты перехвата 80/443, sniffer, панель, secret.
- `Fastest` и `Заблок. сервисы` (include-all): `reality-us` автоматически появится
  в них как РУЧНАЯ опция (не дефолт) — это и есть переключение NL↔US из панели.
- **Запасное ядро Xray — вне скоупа**: сплита US/NL на нём нет; при переходе
  `xkeen -xray` весь whitelist (включая AI) идёт через NL, US-only AI-сервисы
  при этом НЕ РАБОТАЮТ — xray не является рабочим fallback для AI-сценария.

## План деплоя (роутер, по циклу AGENTS.md: бэкап → применить → проверить)

0. Владелец передаёт vless:// US-ноды → заполнить плейсхолдеры (секреты только
   на роутере, в репо — шаблон).
1. Бэкап: `xkeen -mb` на роутере + копия действующего `/opt/etc/mihomo/config.yaml`
   в `backups/20261015-us-ai/` локально (backups/ в .gitignore).
2. Правка `/opt/etc/mihomo/config.yaml` (изменения 1–5, 8) и
   `mihomo/us-pool.list` → `/opt/etc/mihomo/us-pool.list`.
3. `xkeen -mtest` — синтаксис (parse-only, урок итерации 5 спеки 001).
4. `xkeen -restart`.
5. Приёмка — по критериям ниже.
6. Синхронизация репо: шаблон, us-pool.list, решение в AGENTS.md, эта спека.

## Критерии приёмки (живая система)

1. Лог mihomo: нет `initial rule provider ... error`; у КАЖДОГО провайдера
   ruleCount > 0 (включая us-pool@classical).
2. zashboard (`http://192.168.1.1:9090/ui`): `reality-us` виден, delay-тест
   зелёный; US-Fallback = reality-us; состав группы US-Fallback — ровно
   [reality-us, reality-home], БЕЗ DIRECT (иначе тихий fail-open); группа AI
   по дефолту = US-Fallback (NB: store-selected — если в AI раньше выбирали
   вручную, дефолт не применится до ручного переключения).
3. chatgpt.com и claude.ai открываются; в Connections эти домены в цепочке
   US-Fallback/reality-us.
4. YouTube/Meta-соединения — по-прежнему reality-home (не мигнули).
5. Failover (способ по ситуации: приостановить US-ноду у провайдера ИЛИ
   временно подставить нерезолвящийся адрес в `reality-us.server` +
   `xkeen -restart`) → через ~2–3 мин (3×60 c) цепочка AI = reality-home;
   вернуть US → автоматический возврат на reality-us.
6. Основной fallback не тронут: группа Fallback = [reality-home, DIRECT].
7. `grep -n '<' config.yaml` — только ожидаемые литералы (нет незаполненных
   плейсхолдеров; урок итерации 5: mtest литерал-плейсхолдеры не ловит).
8. (Опционально) контрольная перезагрузка роутера: file-провайдер us-pool
   поднимается автозагрузкой — ruleCount > 0 после старта (урок C спеки 001).

## Field-checks / риски

- `path` file-провайдера резолвится от каталога запуска mihomo (флаг `-d`;
  XKeen должен стартовать ядро с `-d /opt/etc/mihomo`) — подтвердить загрузкой
  в логе (ruleCount > 0); при неудаче — абсолютный путь.
- Покрытие category-ai-!cn: входит ли chatgpt.com, oaistatic.com,
  oaiusercontent.com, claude.ai, claudeusercontent.com, api.openai.com,
  api.anthropic.com (Codex/Claude Code CLI). Проверить по Connections;
  промахи → дописать в us-pool.list + reload из панели.
- **adlist REJECT стоит ВЫШЕ us-pool/category-ai**: если нужный AI-домен
  (statsig, sentry, auth0, segment) окажется в рекламном списке, дописывание
  его в us-pool.list НЕ поможет — REJECT сработает раньше. Выход: точечное
  правило ДО adlist (первым правилом `DOMAIN-SUFFIX,<домен>,AI`) — отдельное
  решение по факту находки.
- Горячий reload us-pool из zashboard (Rule Providers → «обновить»): убедиться,
  что file-провайдер реально перечитывает файл с диска.
- Fallback без DIRECT: обе ноды вниз → AI-трафик ошибок соединения (осознанно,
  решение 2); YouTube/Instagram при этом живут по своей цепочке NL → DIRECT.
- Health-check gstatic через US-выход должен работать (иначе fallback ложно
  переключит на NL).
- RAM: +1 прокси — незначительно (замер из спеки 001 актуален).

## Откат

Восстановить `/opt/etc/mihomo/config.yaml` из бэкапа шага 1 → `xkeen -restart`.
Остаточный `us-pool.list` на роутере безвреден (провайдер без правила).
Аварийный случай — как в спеке 001 (xkeen -stop / перезагрузка роутера).
