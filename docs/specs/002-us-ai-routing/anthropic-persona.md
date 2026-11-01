# Дополнение: Anthropic и верификация Persona

Дата: 2026-10-30.

## Требования и согласование

Владелец просит направить сайты Anthropic и его проверки личности через США.
Уточнение владельца: названия могли быть напечатаны неверно; добавлять то,
что использует Anthropic. Согласованное действие — обновить US-пул и применить
на роутере после бэкапа с горячим перечитыванием провайдера.

Persona — партнёр Anthropic для проверки личности, домен `withpersona.com`.
`persona.com` выставлен на продажу; принадлежность `whispersona.com` не подтверждена.

## Решение

Добавить DOMAIN-SUFFIX для withpersona.com и всех доменов из списка anthropic
v2fly/domain-list-community (снимок 2026-10-30); CDN
servd-anthropic-website.b-cdn.net добавить как точный DOMAIN.
Суффиксы покрывают API, SDK, CDN, inquiry и остальные поддомены Persona.
Существующий провайдер us-pool@classical направляет их в AI → US-Fallback.
При недоступности US действует согласованный fallback NL.

Альтернативы: только category-ai не покрывает Persona; маршрутизация общих
CDN целиком избыточна; поэтому выделенный CDN задаётся точным именем.

## Проверки и откат

1. Сохранить рабочий us-pool.list в backups/ и на роутере.
2. Проверить формат, отсутствие дубликатов, сохранение Stripe и наличие всех
   согласованных доменов. Это изменение данных существующего провайдера.
3. Заменить файл и вызвать PUT /providers/rules/us-pool%40classical через
   локальный API Mihomo (не RCI); секрет остаётся на роутере.
4. Проверить ruleCount, AI = US-Fallback и US-Fallback = reality-us.
5. Проверить живое соединение к Persona через прокси и выбранную цепочку.
   Завершение проверки личности подтверждает владелец в браузере.
6. Откат: восстановить сохранённый файл и повторить PUT провайдера.

adlist выше US-пула: если обнаружится REJECT нужного адреса, требуется
отдельное согласование точечного правила. Список доменов не гарантирует
охват всех неизвестных сторонних зависимостей.

## Источники

- https://support.claude.com/en/articles/14328960-identity-verification-on-claude
- https://docs.withpersona.com/security
- https://docs.withpersona.com/tutorial-embedded-flow-inquiry-template
- https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/anthropic
- https://persona.com (проверен: страница продажи домена)

ADR: не требуется — расширение данных существующего US-провайдера.
