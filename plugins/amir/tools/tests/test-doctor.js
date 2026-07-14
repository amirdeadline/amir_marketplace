'use strict';

const assert = require('node:assert/strict');
const { describe, it } = require('node:test');
const fs = require('fs');
const path = require('path');
const { runDoctor, detectCycles } = require('../doctor');
const { makeTempProject, addTask } = require('../lib/test-fixture');

describe('doctor checks', () => {
  it('detects circular dependencies', () => {
    const cycles = detectCycles([
      { id: 'T001', dependencies: ['T002'] },
      { id: 'T002', dependencies: ['T003'] },
      { id: 'T003', dependencies: ['T001'] },
    ]);
    assert.ok(cycles.length > 0);
  });

  it('flags size_estimate caps', () => {
    const root = makeTempProject();
    addTask(root, {
      id: 'T010',
      status: 'pending',
      size_estimate: { files: 8, loc: 120 },
    });

    const findings = runDoctor(root);
    const sizeFinding = findings.find((f) => f.check === 'size_estimate_exceeded');
    assert.ok(sizeFinding);
    assert.equal(sizeFinding.severity, 'HIGH');
  });

  it('flags circular dependencies in project', () => {
    const root = makeTempProject();
    addTask(root, { id: 'T001', status: 'pending', dependencies: ['T002'] });
    addTask(root, { id: 'T002', status: 'pending', dependencies: ['T001'] });

    const findings = runDoctor(root);
    const cycleFinding = findings.find((f) => f.check === 'circular_dependencies');
    assert.ok(cycleFinding);
    assert.equal(cycleFinding.severity, 'CRITICAL');
  });

  it('detects orphan agent workspaces', () => {
    const root = makeTempProject();
    const orphan = path.join(root, 'ai', 'agents', 'dev-orphan');
    fs.mkdirSync(orphan, { recursive: true });
    fs.writeFileSync(path.join(orphan, 'notes.md'), 'orphan');

    const findings = runDoctor(root);
    const orphanFinding = findings.find((f) => f.check === 'orphan_agent_workspace');
    assert.ok(orphanFinding);
  });
});
