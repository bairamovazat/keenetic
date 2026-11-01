# REALITY между свежим Xray-core (3x-ui) и mihomo: несовместимость X25519MLKEM768

Разобрано: 2026-11-01. Контекст: смена KZ-ноды (см. AGENTS.md, решение от 2026-11-01,
и docs/specs/003-kz-ai-routing/). Роутер: Keenetic Ultra, XKeen 2.0, ядро mihomo v1.19.31.

## Симптом

VLESS+Reality (flow=xtls-rprx-vision, fp=firefox из ссылки панели) к серверу 3x-ui
на Xray-core **v26.6.27**: xray-клиент подключается, mihomo — нет. В логе ядра повторяется
`REALITY authentication failed`. Сервер при этом живой и другие ClientHello принимает:
проблема не в ноде и не в ключах из ссылки.

## Что изменилось в Xray-core (таймлайн)

| Версия | Дата | Что произошло |
|---|---|---|
| v25.5.16 | 16.05.2025 | В REALITY добавлен пост-квантовый обмен **X25519MLKEM768** (opt-in на обеих сторонах). Всё совместимо. |
| v26.6.x → v26.7.11 | лето 2026 | Сервер начал отвергать ClientHello, из которого ML-KEM «вырезан». Именно это mihomo делает по умолчанию. Мейнтейнер mihomo официально считает границей **v26.7.11+** (Xray-core#6477). Наш сервер v26.6.27 (27.06.2026) уже в ломающей зоне. |
| v26.9.8 | 08.09.2026 | Жёсткий разрыв (XTLS/REALITY `8cdf7bf9`, vendored `47cfe99`): hello без X25519MLKEM768 в key_share вообще не считается REALITY-подключением, сервер молча уходит в fallback. |
| — | 10.09.2026 | mihomo закрыл issue #3193 как *not planned*: «совместимость с Xray v26.7.11+ не рассматриваем». Фикса в mihomo не будет. |

## Механика

1. mihomo по умолчанию **вырезает** группу X25519MLKEM768 из ClientHello
   (`BuildRemovedX25519MLKEM768HandshakeState` — «для совместимости со старыми REALITY-серверами»).
   Свежий Xray-core считает такой hello «странным/устаревшим» и не распознаёт подключение как REALITY.
2. Опция `reality-opts.support-x25519mlkem768: true` отключает вырезание — но фингерпринт
   должен сам содержать эту группу. На utls v1.8.7 (пин mihomo v1.19.31):
   - `chrome` = HelloChrome_133 — **ML-KEM есть** ✅
   - `firefox` = HelloFirefox_120 — группы нет, опция не помогает ❌ (также safari/ios/edge и пр.)
3. Поэтому `fp=firefox` из vless://-ссылки 3x-ui для mihomo бесполезен. А сама опция —
   mihomo-специфичная, в vless://-ссылках **не передаётся** (3x-ui#6555): импорт ссылки
   «из коробки» у mihomo-клиентов ломается.

## Эмпирическая матрица (проверено живьём с роутера против сервера 26.6.27)

| Клиент | fingerprint | ML-KEM в hello | Результат |
|---|---|---|---|
| xray 26.3.27, supportX25519MLKEM768=true | firefox (библ. xray) | да | ✅ 204 / 0.76 с |
| xray 26.3.27, флаг выкл | firefox | нет (натуральный hello) | ✅ 204 / 0.64 с |
| mihomo + `support-x25519mlkem768: true` | **chrome** | да | ✅ 204 / 1.02 с |
| mihomo без опции | chrome | вырезан mihomo | ❌ auth failed |
| mihomo без опции | firefox | нет (старый FF120) | ❌ auth failed |
| mihomo + опция | firefox | нет — FF120 не умеет | ❌ auth failed |

Вывод: сервер принимает и «натуральные» hello без ML-KEM (xray), но отвергает «вырезанные» (mihomo).

## Рабочее решение (в проде с 2026-11-01)

```yaml
  - name: reality-kz            # имя сохранено, группы не менялись
    type: vless
    # ... server/port/uuid/sni — из vless://-ссылки
    client-fingerprint: chrome          # НЕ firefox из ссылки!
    reality-opts:
      public-key: <PBK>
      short-id: <SID>
      support-x25519mlkem768: true      # опция mihomo, вписывается руками
```

- Проверено сообществом и против v26.9.8+: апгрейд сервера решение не сломает.
- Если mihomo когда-нибудь поднимет utls до 1.9 (HelloFirefox_148 с ML-KEM), firefox снова заработает.
- Запасные варианты: вторая ссылка панели vless+**ws+tls** (работает с любым fp, но без vision-flow
  и с оверхедом WebSocket — использовалась как промежуточная 2026-11-01, затем убрана);
  откат Xray-core на сервере до ≤ v26.5.x — не рекомендуется (потеря обновлений, 3x-ui вернёт ядро).

## Ссылки

- MetaCubeX/mihomo#3193 — разбор + таблица фингерпринтов (closed as not planned)
- XTLS/Xray-core#6477 — «v26.7.11 несовместим с mihomo», ответ: включить опцию
- MHSanaei/3x-ui#6555 — опция не переносится в vless://-ссылки
- wiki.metacubex.one → Proxies → TLS → `reality-opts.support-x25519mlkem768`
