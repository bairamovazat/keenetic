"""Контракт конфигурации (003 + однонодовая схема 2026-11-01).
Запуск: python3 -m unittest discover -s mihomo -p 'test_*.py'.
Рабочий конфиг роутера проверять так:
  KZ_CONFIG=<файл> python3 -m unittest discover -s mihomo -p 'test_*.py'
"""
import os
from pathlib import Path
import re
import unittest

import yaml

ROOT = Path(__file__).resolve().parent
SUFFIXES = '''ant.dev anthropic.com anthropic.team antspace.dev chatbotclaude.com
clau.de claude.ai claude.app claude.com claude.dev claude.new claude.site
claudeacademy.com claudemcpclient.com claudemcpcontent.com claudepages.dev
claudestudio.com claudeusercontent.com withpersona.com frompersona.com yoti.com
stripe.com stripecdn.com stripe.network stripe.dev stripe.events stripe.global
link.com hcaptcha.com'''.split()
EXACT = '''servd-anthropic-website.b-cdn.net http-intake.logs.us5.datadoghq.com
browser-intake-us5-datadoghq.com'''.split()


class RoutingContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = yaml.safe_load(Path(os.getenv('KZ_CONFIG', ROOT / 'config.yaml.template')).read_text())
        cls.groups = {g['name']: g for g in cls.config['proxy-groups']}
        path = ROOT / 'kz-pool.list'
        cls.entries = [l.strip() for l in path.read_text().splitlines()
                       if l.strip() and not l.lstrip().startswith('#')] if path.exists() else []

    def covered(self, host):
        for entry in self.entries:
            kind, domain = entry.split(',')
            if host == domain or (kind == 'DOMAIN-SUFFIX' and host.endswith('.' + domain)):
                return True
        return False

    def test_ai_has_only_kz(self):
        ai = self.groups['AI']
        self.assertEqual(ai['type'], 'select')
        self.assertEqual(ai['proxies'], ['reality-kz'])
        for key in ('include-all', 'include-all-proxies', 'include-all-providers', 'use'):
            self.assertFalse(ai.get(key), key)

    def test_domain_matrix_and_boundaries(self):
        self.assertTrue(self.entries)
        self.assertEqual(len(self.entries), len(set(self.entries)))
        self.assertEqual(len(self.entries), len(SUFFIXES) + len(EXACT))
        for e in self.entries:
            self.assertRegex(e, r'^(DOMAIN|DOMAIN-SUFFIX),[a-z0-9.-]+$')
        for domain in SUFFIXES:
            for host in (domain, 'nested.test.' + domain):
                with self.subTest(host=host):
                    self.assertTrue(self.covered(host), host)
        for host in EXACT:
            self.assertTrue(self.covered(host), host)
            self.assertFalse(self.covered('unrelated.' + host), host)
        for host in ('notclaude.ai', 'stripe.com.example.org', 'example.com',
                     'accounts.google.com', 'fonts.gstatic.com', 'cdn.jsdelivr.net',
                     'maps.googleapis.com', 'www.youtube.com', 'i.instagram.com'):
            self.assertFalse(self.covered(host), host)
        old = ROOT / 'us-pool.list'
        for line in old.read_text().splitlines():
            if line.startswith('DOMAIN') and 'example.invalid' not in line:
                self.assertIn(line, self.entries)

    def test_priority_and_references(self):
        rules = self.config['rules']
        # Порядок: QUIC REJECT → kimi.ai DIRECT → kz-pool AI → category-ai AI →
        # adlist REJECT → .kz через KZ (после adlist: реклама .kz режется раньше) → сервисы.
        self.assertEqual(rules[:6], ['RULE-SET,quic@inline,REJECT',
                                     'DOMAIN-SUFFIX,kimi.ai,DIRECT',
                                     'RULE-SET,kz-pool@classical,AI',
                                     'RULE-SET,category-ai@domain,AI',
                                     'RULE-SET,adlist@domain,REJECT',
                                     'DOMAIN-SUFFIX,kz,reality-kz'])
        self.assertEqual(rules[-1], 'MATCH,DIRECT')  # blacklist-политика: вне списков — напрямую
        providers = self.config['rule-providers']
        self.assertEqual(providers['quic@inline']['payload'], ['AND,((DST-PORT,443),(NETWORK,UDP))'])
        self.assertEqual(providers['kz-pool@classical'], {
            'type': 'file', 'behavior': 'classical', 'format': 'text',
            'path': '/opt/etc/mihomo/kz-pool.list'})
        targets = set(self.groups) | {p['name'] for p in self.config['proxies']} | {'DIRECT', 'REJECT'}
        for rule in rules:
            self.assertIn(rule.rsplit(',', 1)[-1], targets)
            for provider in re.findall(r'RULE-SET,([^,)]+)', rule):
                self.assertIn(provider, providers)

    def test_single_node_no_fallback(self):
        """Однонодовая схема (2026-11-01): только reality-kz, без NL/US/fallback (fail-closed)."""
        proxies = {p['name'] for p in self.config['proxies']}
        self.assertEqual(proxies, {'reality-kz'})  # NL удалена полностью, US не осталось
        for gone in ('Fallback', 'Fastest', 'VK', 'US-Fallback'):
            self.assertNotIn(gone, self.groups, gone)
        # Всякая группа — одновариантная [reality-kz]: выбора нод нет, только метки сервисов.
        for name, group in self.groups.items():
            self.assertEqual(group['type'], 'select', name)
            self.assertEqual(group['proxies'], ['reality-kz'], name)
            for key in ('include-all', 'include-all-proxies', 'include-all-providers', 'use'):
                self.assertFalse(group.get(key), (name, key))
        # Нигде в АКТИВНОМ конфиге не осталось ссылок на удалённые ноды (комментарии-история не в счёт).
        all_names = set(self.groups) | proxies
        self.assertNotIn('reality-home', all_names)
        self.assertNotIn('reality-us', all_names)
        # Никакого автоматического ухода в DIRECT при падении KZ (fail-closed).
        raw = Path(os.getenv('KZ_CONFIG', ROOT / 'config.yaml.template')).read_text()
        self.assertNotIn('type: fallback', raw)
        self.assertNotIn('type: url-test', raw)

    def test_kz_transport(self):
        kz = {p['name']: p for p in self.config['proxies']}['reality-kz']
        # С 2026-11-01 KZ-нода на Xray-core 26.6.27+ (3x-ui): строго chrome + ML-KEM768
        # (firefox-fp из vless://-ссылки в mihomo не работает — HelloFirefox_120 без ML-KEM).
        for key, value in {'type': 'vless', 'port': 443, 'tls': True,
                           'flow': 'xtls-rprx-vision', 'client-fingerprint': 'chrome'}.items():
            self.assertEqual(kz[key], value)
        self.assertNotIn('network', kz)  # tcp (reality), не ws
        self.assertNotIn('ws-opts', kz)
        self.assertIs(kz['reality-opts'].get('support-x25519mlkem768'), True)
        if not os.getenv('KZ_CONFIG'):
            self.assertEqual(kz['uuid'], '<KZ_UUID>')
            self.assertEqual(kz['reality-opts'], {'public-key': '<KZ_PBK>',
                                                  'short-id': '<KZ_SID>',
                                                  'support-x25519mlkem768': True})


if __name__ == '__main__':
    unittest.main()
