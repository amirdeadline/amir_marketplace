'use strict';

const assert = require('node:assert/strict');
const { describe, it } = require('node:test');
const path = require('path');
const { scanPath } = require('../secrets_scan');

describe('secrets scan', () => {
  it('detects planted fake secrets', () => {
    const planted = path.join(__dirname, 'fixtures', 'planted-secrets.txt');
    const findings = scanPath(planted);
    const types = new Set(findings.map((f) => f.type));
    assert.ok(types.has('aws_access_key'));
    assert.ok(types.has('github_token'));
  });

  it('passes clean file', () => {
    const clean = path.join(__dirname, 'fixtures', 'clean.txt');
    const findings = scanPath(clean);
    assert.equal(findings.length, 0);
  });
});
