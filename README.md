# keenetic — домашняя сеть на Keenetic Ultra (KN-1811)

Рабочий репозиторий для управления домашним роутером **Keenetic Ultra (KN-1811)** (192.168.1.1,
KeeneticOS 5.x, mesh из 3 узлов): VPN через VLESS (XKeen/Xray), сетевое хранилище, торрент-клиент,
SSH, Entware/OPKG, кастомизации и прошивка.

## Карта репозитория

| Путь | Что |
|---|---|
| `AGENTS.md` | **Главный файл**: принципы работы с роутером, правила безопасности, решения. Читается агентом автоматически |
| `docs/router.md` | Паспорт устройства и текущее состояние сети |
| `docs/xkeen-vless.md` | План настройки XKeen (VLESS/Xray) — основной VPN |
| `docs/sources.md` | Официальные доки, инструкции сообщества, готовые инструменты |
| `scripts/rci.sh` | Обёртка над RCI API роутера (пароль — интерактивно) |
| `backups/` | Бэкапы running-config (в .gitignore, в git не попадают) |

## Быстрый старт

```bash
# проверить, что роутер доступен (ожидаем HTTP 200/401)
curl -s -o /dev/null -w '%{http_code}\n' http://192.168.1.1/

# опросить RCI API (логин/пароль спросит)
scripts/rci.sh show/version
```

## Статус

- [x] Инициализация репозитория, ресёрч источников и инструментов
- [ ] Первый RCI-опрос (`show version`, компоненты) → заполнение `docs/router.md`
- [ ] Включить SSH (Keenetic «Сервер SSH» или Entware)
- [ ] Бэкап конфига
- [ ] USB-накопитель (EXT4+SWAP) → Entware (aarch64)
- [ ] XKeen 2.0 (форк JamesZero) + VLESS/REALITY
- [ ] SMB-хранилище, Transmission
