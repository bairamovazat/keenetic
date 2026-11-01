# Review-log: AI-трафик через US-ноду (002)

Хроника валидаций спеки (Стандарты 0/3). Валидатор: агент `reviewer`
(DeepSeek V4 Pro), финальный гейт `reviewer-final` — по необходимости.

## Итерация 1 — 2026-10-15 — отправлено на валидацию

Что валидируется: `spec.md` + эталон `mihomo/config.yaml.template` (спека меняет
его пункты 1–5, 7 и добавляет файл `mihomo/us-pool.list`).

Суть решения: второй прокси reality-us (US); вся группа AI (category-ai + свой
file-провайдер us-pool.list) идёт через скрытую fallback-группу US-Fallback =
[reality-us, reality-home] (без DIRECT); основной пул не меняется
(Fallback = [reality-home, DIRECT]); список US-доменов — отдельный файл в репо,
hot-reload из zashboard.

Альтернативы (отвергнуты владельцем 2026-10-15):
- точечный список OpenAI+Anthropic вместо всего category-ai — отвергнут: владелец
  хочет весь AI на US;
- US → NL → DIRECT — отвергнуто: для AI DIRECT бессмыслен;
- inline-список в config.yaml — отвергнут: правка большого конфига + рестарт ядра;
- NL → US → DIRECT для основного пула — отвергнуто: «остальной трафик через NL».

Результат: **APPROVE_WITH_NOTES**. Блокеров нет; механика fallback-без-DIRECT
(findAliveProxy → proxies[0] при всех мёртвых), file-провайдер (type: file +
behavior: classical + format: text — format обязателен, дефолт yaml парсил бы
.list как YAML и ронял провайдер) и порядок include-all (дописывает после
явного списка, parser.go) подтверждены против исходников mihomo.

### Замечания — все закрыты правками спеки в этой же итерации

1. Неверное обоснование отказа от include-all у US-Fallback («DIRECT первым
   кандидатом») → переписано: include-all дописывает DIRECT в конец → после
   падения обеих нод тихий fail-open, что запрещает решение 2. Пункт 8
   изменений: заодно поправить неточную формулировку комментария у основного
   Fallback в шаблоне.
2. Противоречие «все сервисные группы не меняются» vs смена дефолта AI →
   добавлено «кроме группы AI».
3. Воркфлоу правки us-pool.list: панель не редактирует файл — разведено
   (репо → scp/SSH на роутер → reload в zashboard), пункт 7 изменений.
4. adlist REJECT выше us-pool: домен из рекламного списка дописыванием в
   us-pool не спасти → в риски добавлен выход (точечное правило ДО adlist).
5. flow/fp захардкожены → в изменения добавлена проверка ссылки US-ноды
   (vision + chrome).
6. Способ failover-теста не определён → в критерий 5 (приостановка у
   провайдера или нерезолвящийся server + restart).
7. Xray-компромисс усилен: US-only AI на xray НЕ работает, xray — не рабочий
   fallback для AI.
8. Контрольная перезагрузка → опциональный критерий 8 (file-провайдер и
   автозагрузка).
9. store-selected может перебить новый дефолт AI → помечено в критерии 2.
10. Толерантность `#`-комментариев в text-списке статически не доказана →
    покрывается критерием 1 (ruleCount > 0, нет provider error).

### Вопросы к владельцу (открыты, нужны до деплоя)

1. US-нода — собственный VPS или подписка провайдера? (определяет способ
   failover-теста из критерия 5).
2. Подтверждить: vless:// US-ноды = `flow=xtls-rprx-vision` + `fp=chrome`
   (зеркало reality-home)?
3. Правка us-pool.list на роутере приемлема через Entware SSH (vi/nano) или
   scp с управляющего Mac?

### FIELD_CHECKS валидатора (добавлены в спеку)

- Разрешение path file-провайдера от HomeDir (флаг `-d` XKeen), не от
  каталога конфига — подтвердить фактом загрузки.
- Горячий reload file-провайдера реально перечитывает файл с диска.
- Явная проверка СОСТАВА US-Fallback (ровно [reality-us, reality-home], без
  DIRECT) — иначе тихий fail-open.
- Фактический дефолт AI после применения (store-selected).
- Покрытие category-ai-!cn по Connections; health-check gstatic через US.

## Статус: СПЕКА ОДОБРЕНА ВАЛИДАТОРОМ (APPROVE_WITH_NOTES), правки внесены.

Ожидает валидации владельцем и vless://-ссылки US-ноды. На роутер ничего
не применено.

## Деплой и приёмка — 2026-10-15 — ПРИНЯТО

Инцидент перед деплоем: SSH dropbear на роутере не отвечал (порты 22/222/2222
закрыты при живом Entware/mihomo; последний рабочий доступ 2026-10-01).
Вылечено перезагрузкой роутера владельцем (автозагрузка Entware подняла
dropbear). Заметка в docs/router.md.

Ответы владельца на вопросы итерации 1: US-нода — собственный VPS
(cactus9-sub.azooov.ru, EWR); ссылка `flow=xtls-rprx-vision` + `fp=chrome`
подтверждена; правки us-pool.list — через SSH (vi/scp).

Ход деплоя (по плану спеки): бэкап `xkeen -mb` (2026-10-15_15-57_configs_mihomo)
+ локальная копия `backups/20261015-us-ai/config.yaml.orig` (md5 с роутером
сверен) → правка копии → локальная YAML-валидация (методика итерации 3 спеки
001: провайдеры ↔ правила, составы групп, порядок us-pool перед category-ai) →
загрузка config.yaml + us-pool.list → `xkeen -mtest` OK → `xkeen -restart`.
Рабочая копия с секретами: `backups/20261015-us-ai/config.yaml.new` (gitignore).

Критерии приёмки — все выполнены:
1. 21 провайдер загружен, пустых нет; us-pool@classical ruleCount=1
   (#-комментарии в text-списке переносятся нормально — field-check закрыт).
2. US-Fallback: all=[reality-us, reality-home] (DIRECT отсутствует — явная
   проверка состава), now=reality-us, delay 179 мс (gstatic через US);
   reality-home delay 57 мс. AI → US-Fallback (store-selected не помешал —
   в группе AI ранее ручных выборов не было).
3. chatgpt.com и claude.ai: выход 82.38.60.165, colo=EWR, loc=US; в Connections
   chatgpt.com / ws.chatgpt.com / ab.chatgpt.com / chat.openai.com /
   persistent.oaistatic.com / codex-cloud-{backend,environments}.chatgpt.com —
   все в цепочке AI→US-Fallback→reality-us (эндпоинты Codex покрыты
   category-ai без дописок в us-pool).
4. www.youtube.com и i.ytimg.com → YouTube→Заблок. сервисы→Fallback→reality-home;
   i.instagram.com / graph.instagram.com / scontent-*.cdninstagram.com /
   edge-mqtt.facebook.com → Meta→…→reality-home. Основной пул не мигнул.
5. Failover: подмена server у reality-us на нерезолвящийся + restart →
   US-Fallback.now=reality-home через ~20 с; chatgpt.com/cdn-cgi/trace показал
   выход 72.56.118.18 (AMS, NL) — AI реально ушёл на NL. Восстановление
   конфига (md5 сверен) + restart → now=reality-us, выход снова EWR.
6. Fallback (основной) = [reality-home, DIRECT], now=reality-home — не тронут.
7. `grep '<'` — только комментарии/якоря, незаполненных плейсхолдеров нет.
8. Холодная перезагрузка НЕ выполнялась (роутер перезагружался до деплоя,
   в рамках инцидента с SSH): загрузка us-pool подтверждена рестартом ядра
   (xkeen -restart читает конфиг и файл-провайдер с диска); автозагрузка
   file-провайдера покрывается тем же механизмом. Осознанный компромисс —
   без дополнительного окна простоя.

Дополнительно (field-check из спеки): hot-reload us-pool.list — добавление
строки на роутере + PUT /providers/rules/us-pool@classical (HTTP 204) →
ruleCount 1→2; откат файла + reload → 1. Ядро не рестартировалось. Рабочий
воркфлоу правки списка подтверждён.

Синхронизация репо: config.yaml.template (идентичен деплою структурно,
проверено скриптом), mihomo/us-pool.list (md5 = роутер), AGENTS.md (решение
2026-10-15), статус спеки. Изменения не закоммичены (владелец коммитит сам);
в git также висит незакоммиченная запись о QUIC от 2026-10-01 (прошлая сессия).
