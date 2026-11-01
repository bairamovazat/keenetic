# Источники и матрица доменов

Проверено 2026-10-30. Поисковый инструмент возвращает HTTP 403; использованы
прямые первоисточники и их ссылки. Список — подтверждённые публичные зависимости,
не утверждение о полноте динамического флоу конкретного аккаунта.

## Верификация Anthropic

- [Identity verification](https://support.claude.com/en/articles/14328960-identity-verification-on-claude):
  **Persona Identities**, физический ID, при необходимости selfie; также KYB.
- [Age assurance](https://support.claude.com/en/articles/15171100-age-assurance-on-claude):
  **Yoti**, оценка возраста по лицу, документ или Digital ID. Это отдельная
  проверка, не Persona и не основание добавлять непроверенные Jumio/Onfido/Sumsub.
- [Persona security](https://docs.withpersona.com/security): все публичные
  allowlist-хосты под withpersona.com: app, cdn, inquiry, miniapp, sdk, t,
  webrtc-consumer, webrtc-stun, пользовательские поддомены. frompersona.com —
  почтовый домен; добавляем для HTTP-ссылок, маршрутизация SMTP не заявляется.
- [Persona SDK](https://docs.withpersona.com/tutorial-embedded-flow-inquiry-template):
  cdn.withpersona.com/dist/persona-*.js, API api.withpersona.com.
- [Официальный Yoti SDK](https://github.com/getyoti/yoti-node-sdk): hub.yoti.com,
  support.yoti.com, developers.yoti.com; первичный охват yoti.com со всеми поддоменами.
  Полный динамический список Yoti требует живой сессии; developers.yoti.com
  отдаёт JS-оболочку, поэтому неизвестные CDN не выдумываются.

## Stripe / антифрод

- [Официальные домены](https://docs.stripe.com/ips): stripe.com, stripecdn.com,
  stripe.network и **hcaptcha.com**. Поддомены js/api/checkout/billing/buy/pay/
  payments/hooks/m/q/r/verify/uploads покрываются суффиксами.
- [CSP Stripe](https://docs.stripe.com/security/guide): **link.com** и все
  поддомены (checkout.link.com/statics.link.com), maps.googleapis.com (Address Element).
- [hCaptcha CSP](https://docs.hcaptcha.com/): нужны корневой домен и все
  поддомены, нельзя фиксировать только текущий newassets.
- [v2fly Stripe](https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/stripe):
  дополнительно stripe.dev, stripe.events, stripe.global и
  stripe-terminal-local-reader.net. Последний — локальные терминалы, не нужен
  интернет-оплате Claude и не включается.
- Банковские ACS/3DS-редиректы зависят от карты/банка; маршрутизация всех банков
  не выводится из списка Stripe. Не выполнять платёж ради поиска доменов.

## Anthropic и веб-зависимости

- [v2fly Anthropic](https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/anthropic):
  ant.dev, anthropic.com, anthropic.team, antspace.dev, chatbotclaude.com,
  clau.de, claude.ai, claude.app, claude.com, claude.dev, claude.new, claude.site,
  claudeacademy.com, claudemcpclient.com, claudemcpcontent.com, claudepages.dev,
  claudestudio.com, claudeusercontent.com; точный servd-anthropic-website.b-cdn.net.
- [Desktop network](https://code.claude.com/docs/en/desktop#network-access-requirements):
  api/a-api/a-cdn/s-cdn/assets-proxy.anthropic.com, platform/sso.claude.com,
  assets/downloads/livepreview.claude.ai, bridge/frame.claudeusercontent.com —
  покрываются родительскими суффиксами.
- [Code network](https://code.claude.com/docs/en/network-config): отдельные точные
  http-intake.logs.us5.datadoghq.com, browser-intake-us5-datadoghq.com (телеметрия);
  fonts.googleapis.com, fonts.gstatic.com; библиотеки артефактов:
  cdnjs.cloudflare.com, cdn.jsdelivr.net, cdn.tailwindcss.com, code.jquery.com, unpkg.com.
  Их HTTP-трафик переводится на KZ и при использовании другими сайтами тоже.
- [Вход](https://support.claude.com/en/articles/13189465-log-in-to-your-claude-account):
  Google или email magic link, mail.anthropic.com покрыт. Точный
  accounts.google.com включаем для Google OAuth, не весь Google/YouTube.
  Корпоративные внешние SSO/почтовые провайдеры индивидуальны и не перечислены.

## Матрица обязательного покрытия для тестов

Суффиксы: весь список v2fly Anthropic выше + withpersona.com, frompersona.com,
yoti.com, stripe.com, stripecdn.com, stripe.network, stripe.dev, stripe.events,
stripe.global, link.com, hcaptcha.com.

Точные: servd-anthropic-website.b-cdn.net, http-intake.logs.us5.datadoghq.com,
browser-intake-us5-datadoghq.com.

**Итоговое решение владельца после reviewer: только сервисные домены.**
Google OAuth/Maps/Fonts и CDN библиотек выше — найденные зависимости, но
исключены из KZ-пула, сохраняют текущие маршруты и не входят в KZ-only гарантию.
Телеметрия включена только двумя точными документированными intake-хостами,
не всем datadoghq.com. hCaptcha остаётся как документированная зависимость Stripe.

category-ai остаётся динамическим провайдером всех остальных AI. Для критичных
Claude/Anthropic правила продублированы явно, чтобы изменение внешнего списка
не отправило их в MATCH,DIRECT.

## Ограничения исследования

Документация не доказывает, какие опциональные зависимости вызывает конкретный
аккаунт; фактическая верификация и все редиректы проверяются вместе с владельцем.
Общий IP CDN, отсутствие SNI/ECH, DNS-over-HTTPS и STUN не решаются суффиксным
списком. Пользователь после обсуждения выбрал текущий веб-перехват 80/443.
