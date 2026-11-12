"""Bounded offline data/source acceptance; no browser or runtime claims."""
import html
from html.parser import HTMLParser
import json
import re
import runpy
import unittest

B = runpy.run_path(__file__.replace('test-td-region-explainer.py', 'build-td-region-explainer.py'))


class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.ids = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags.append((tag, a))
        if 'id' in a:
            self.ids.append(a['id'])
        if 'href' in a:
            self.links.append(a['href'])


class Acceptance(unittest.TestCase):
    def test_exact_records_and_digests(self):
        archives, s, b, cards = B['load']()
        self.assertEqual([B['sha'](archives[k]['result.json']) for k in B['PINS']], [
            '9caff8648cb2165bf0d0ed7c3e9fd70ce6759d28b0c891b9fd36de1551fac650',
            'd0853fba10ca350e353d9a2786a6362d99f80363aa7b12a071d470b89e56819c'])
        for card, site, identity in zip(cards, ((2944, 13824), (2688, 10880), (5760, 10880)), (-3, -2, -1)):
            self.assertEqual((card['x'], card['z']), site)
            self.assertEqual(card['pr59']['id'], identity)
            r, c = card['row'], card['column']
            self.assertEqual(card['elevation_metres'], json.loads(archives['td-story']['input/visual-data.json'])['elevations'][r][c])
            self.assertIn(card['pr58'], b['histories'])
            t = card['pr59']
            self.assertEqual(t['token'], t['surface_history'])
            self.assertEqual(t['token'], t['deep_history'])
            self.assertEqual(t, next(v for v in s['histories'] if v['id'] == identity))
        rendered = B['build']().decode()
        data = json.loads(html.unescape(re.search(r'<pre id="provenance">(.*?)</pre>', rendered, re.S)[1]))
        self.assertEqual(data['cards'], cards)

    def test_unchanged_maps_with_only_three_marker_links_added(self):
        archives, *_ = B['load']()
        old = re.findall(r'<svg\b.*?</svg>', archives['td-story']['viewer.html'].decode(), re.S)
        new = re.findall(r'<svg\b.*?</svg>', B['build']().decode(), re.S)
        self.assertEqual(len(new), 2)
        for original, annotated in zip(old, new):
            self.assertEqual(re.sub(r'<a href="#card-\d".*?</a>', '', annotated), original)
            self.assertEqual(annotated.count('class="marker"'), 3)
            self.assertEqual(original.count('<circle '), 2401)

    def test_static_content_and_fragment_navigation(self):
        text = B['build']().decode()
        d = Document()
        d.feed(text)
        self.assertEqual(len(d.ids), len(set(d.ids)))
        self.assertEqual([a['id'] for t,a in d.tags if t == 'article'], ['card-1', 'card-2', 'card-3'])
        self.assertFalse(any(t in ('script', 'iframe', 'img', 'link') for t,a in d.tags))
        self.assertTrue(all(link.startswith('#') and link[1:] in d.ids for link in d.links))
        self.assertFalse(any('hidden' in a or 'src' in a or any(k.startswith('on') for k in a) for t,a in d.tags))
        self.assertNotRegex(text, r'(?i)https?://|@import|url\((?!#)|display\s*:\s*none|visibility\s*:\s*hidden')
        for required in ('Negative contact comparison retained', 'did not establish better landscape-related contacts',
                         'Regional summaries · not this point', '±0.5 clamp active', 'Unknown · interpretation abstains',
                         'No depth scale', 'Shared token:', 'PR58 difference-mode edge stencil is unavailable here.'):
            self.assertIn(required, text)
        self.assertEqual(text.count('<h3>Observed here'), 3)
        self.assertIn('article:target', text)
        self.assertIn(':focus-visible', text)

    def test_unsupported_space_never_returns_observation(self):
        archives, *_ = B['load']()
        heights = json.loads(archives['td-story']['input/visual-data.json'])['elevations']
        for x,z in ((2689,10880), (2688,10881), (2687,10880), (5761,13953), (5824,13952), (2688,10816)):
            self.assertIsNone(B['observed_at'](x,z,heights))
        for r,c in B['SITES']:
            self.assertEqual(B['observed_at'](2688+64*c,10880+64*r,heights), heights[r][c])

    def test_corrupt_input_fails_closed(self):
        blobs = {k: (B['ROOT']/('docs/evidence/'+k+'.zip')).read_bytes() for k in B['PINS']}
        for key in blobs:
            bad = dict(blobs)
            bad[key] = bad[key][:-1] + bytes([bad[key][-1] ^ 1])
            with self.assertRaisesRegex(ValueError, 'Immutable input mismatch'):
                B['build'](bad)

    def test_exact_standalone_rebuild(self):
        first = B['build']()
        self.assertEqual(first, B['build']())
        self.assertEqual(first, B['OUTPUT'].read_text(encoding='utf-8').encode('utf-8'))
        self.assertEqual(first, first.decode().replace('\n', '\r\n').replace('\r\n', '\n').encode())


if __name__ == '__main__':
    unittest.main()
