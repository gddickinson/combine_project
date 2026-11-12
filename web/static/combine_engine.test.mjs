// Node test: the JS port must reproduce the Python output byte for byte on the fixture tree
// (tests/fixtures/combine_fixture.json, written by scripts/make_combine_fixture.py). Run: node combine_engine.test.mjs
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { cmpCodepoints, fileText, fnmatch, plan, renderCombined, renderStructure, suffix, timestamp } from './combine_engine.js';

const fx = JSON.parse(readFileSync(new URL('../../tests/fixtures/combine_fixture.json', import.meta.url), 'utf8'));
let n = 0;
const t = (name, fn) => { fn(); n++; console.log('ok', name); };

t('suffix matches pathlib (3.12)', () => {
  for (const [s, e] of [['a.py', '.py'], ['foo.', ''], ['.bashrc', ''], ['..x', '.x'], ['x.tar.gz', '.gz'], ['LICENSE', '']])
    assert.equal(suffix(s), e, s);
});
t('fnmatch', () => {
  assert.ok(fnmatch('foo.egg-info', '*.egg-info'));
  assert.ok(!fnmatch('foo.egg-infox', '*.egg-info'));
  assert.ok(fnmatch('build', 'build') && !fnmatch('Build', 'build'));
  assert.ok(fnmatch('a1', 'a[0-9]') && !fnmatch('a1', 'a[!0-9]') && fnmatch('ab', 'a?'));
});
t('code point ordering', () => {
  assert.ok(cmpCodepoints('z', 'z\u{1F600}') < 0);
  assert.ok(cmpCodepoints('B', 'a') < 0 && cmpCodepoints('a', 'ab') < 0);
});
t('timestamp format', () => assert.equal(timestamp(new Date(2026, 0, 2, 3, 4, 5)), '2026-01-02 03:04:05'));
t('file text', () => {
  assert.equal(fileText(new Uint8Array([0x61, 0x0d, 0x0a, 0x62, 0x0d])), 'a\nb\n');
  assert.equal(fileText(new Uint8Array([0xef, 0xbb, 0xbf, 0x61])), '﻿a\n');
  assert.equal(fileText(new Uint8Array([0x80])), '[Binary file - cannot display content]\n');
  assert.equal(fileText(new Uint8Array([])), '\n');
});

const files = fx.tree.files.map(f => f.path);
const bytes = new Map(fx.tree.files.map(f => [f.path, new Uint8Array(Buffer.from(f.b64, 'base64'))]));
const planned = plan(fx.tree.name, files, fx.tree.dirs, fx.rules);
const texts = new Map(planned.included.map(p => [p, fileText(bytes.get(p))]));

t('structure file equals Python byte for byte', () =>
  assert.equal(renderStructure(fx.tree.name, planned, fx.generated), fx.structure));
t('combined file equals Python byte for byte', () =>
  assert.equal(renderCombined(fx.tree.name, planned, texts, fx.generated), fx.combined));
t('UTF-8 bytes equal', () => {
  const enc = new TextEncoder();
  assert.deepEqual(enc.encode(renderCombined(fx.tree.name, planned, texts, fx.generated)), enc.encode(fx.combined));
});
t('order of input paths does not matter', () => {
  const p2 = plan(fx.tree.name, [...files].reverse(), [...fx.tree.dirs].reverse(), fx.rules);
  assert.deepEqual(p2, planned);
});
console.log(`${n} tests passed`);
