"""Offline data/link checks; no browser or runtime acceptance claim."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import runpy
import unittest

B = runpy.run_path(str(Path(__file__).with_name('build-td-site-atlas.py')))


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tags = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class Atlas(unittest.TestCase):
    def test_every_exact_record(self):
        archives, story, baseline, _ = B['READER']['load']()
        heights = json.loads(archives['td-story']['input/visual-data.json'])['elevations']
        text = B['build']().decode()
        rows = re.findall(r'<tr id="site-(\d+)-(\d+)">(.*?)</tr>', text)
        self.assertEqual(len(rows), 2401)
        for ordinal, (r, c, body) in enumerate(rows):
            r, c = int(r), int(c)
            self.assertEqual((r,c), divmod(ordinal,49))
            cells = re.findall(r'<td>(.*?)</td>', body)
            h = next(v for v in story['histories'] if v['id'] == story['ids'][r][c][0])
            self.assertEqual(cells[:6], [f'r{r},c{c}', f'{2688+64*c}, {10880+64*r}',
                str(heights[r][c]), str(h['mean_contrast_metres']),
                f"{h['id']} / {h['substrate']}", h['authored_event']])
            self.assertEqual(cells[7], 'Abstain; error unknown')

    def test_static_links_and_maps(self):
        text = B['build']().decode()
        tags = Document(text).tags
        ids = [a['id'] for _,a in tags if 'id' in a]
        self.assertEqual(len(ids),len(set(ids)))
        links = [a['href'] for _,a in tags if 'href' in a]
        self.assertTrue(all(v.startswith('#') and v[1:] in ids for v in links))
        self.assertEqual(sum(v.startswith('#site-') for v in links),4802)
        self.assertFalse(any(t in ('script','iframe','img','link') or 'src' in a or
            any(k.startswith('on') for k in a) for t,a in tags))
        original = re.findall(r'<svg\b.*?</svg>', B['READER']['load']()[0]['td-story']['viewer.html'].decode(), re.S)
        actual = re.findall(r'<svg\b.*?</svg>', text,re.S)
        self.assertEqual([re.sub(r'<a\b[^>]*>(.*?)</a>',r'\1',v,flags=re.S) for v in actual],original)

    def test_corruption_rejected(self):
        reader = B['READER']
        blobs = {k:(reader['ROOT']/f'docs/evidence/{k}.zip').read_bytes() for k in reader['PINS']}
        for key in blobs:
            bad = dict(blobs)
            bad[key] = bad[key][:-1]+bytes([bad[key][-1]^1])
            with self.assertRaises(ValueError):
                B['build'](bad)

    def test_canonical_rebuild_and_limits(self):
        raw = B['build']()
        self.assertEqual(raw,B['build']())
        self.assertEqual(raw,B['OUTPUT'].read_text(encoding='utf-8').encode())
        text = raw.decode()
        for phrase in ('no demonstrated geological necessity','error remain unknown',
                       'Geological interpretation abstains everywhere',
                       'not local slopes', 'Dedicated-launcher preparation stays deferred'):
            self.assertIn(phrase,text)


if __name__ == '__main__':
    unittest.main()
