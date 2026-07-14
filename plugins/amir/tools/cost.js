#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const { loadActivityLines } = require('./activity');
const { loadTasks } = require('./state');
const { statePath } = require('./lib/paths');

function loadPricing() {
  const pricingPath = path.join(__dirname, 'pricing.json');
  return JSON.parse(fs.readFileSync(pricingPath, 'utf8'));
}

function estimateTokensFromChars(chars) {
  return Math.ceil(chars / 4);
}

function resolveModelPricing(pricing, model) {
  const models = pricing.models || {};
  if (model && models[model]) return models[model];
  return models.default || { input_per_mtok: 3, output_per_mtok: 15 };
}

function estimateUsd(tokensIn, tokensOut, model, pricing) {
  const rates = resolveModelPricing(pricing, model);
  const inputCost = (tokensIn / 1_000_000) * rates.input_per_mtok;
  const outputCost = (tokensOut / 1_000_000) * rates.output_per_mtok;
  return inputCost + outputCost;
}

function normalizeEventCost(event, pricing) {
  let tokensIn = event.tokens_in ?? 0;
  let tokensOut = event.tokens_out ?? 0;
  let usd = event.usd;

  if (!tokensIn && event.result) {
    tokensIn = estimateTokensFromChars(String(event.result).length);
  }

  if (usd === null || usd === undefined) {
    usd = estimateUsd(tokensIn, tokensOut, event.model, pricing);
  }

  return { tokensIn, tokensOut, usd };
}

function aggregateCosts(projectRoot) {
  const pricing = loadPricing();
  const events = loadActivityLines(projectRoot);
  const tasksData = loadTasks(projectRoot);

  const byTask = new Map();
  const byAgent = new Map();
  const byCycle = new Map();
  const byModel = new Map();
  let projectTotal = { tokensIn: 0, tokensOut: 0, usd: 0 };

  const fixCyclesByTask = new Map();

  for (const event of events) {
    const { tokensIn, tokensOut, usd } = normalizeEventCost(event, pricing);
    projectTotal.tokensIn += tokensIn;
    projectTotal.tokensOut += tokensOut;
    projectTotal.usd += usd;

    const taskId = event.task_id || '_none';
    const agentId = event.agent_id || '_unknown';
    const model = event.model || 'default';

    function bump(map, key) {
      const cur = map.get(key) || { tokensIn: 0, tokensOut: 0, usd: 0, events: 0 };
      cur.tokensIn += tokensIn;
      cur.tokensOut += tokensOut;
      cur.usd += usd;
      cur.events += 1;
      map.set(key, cur);
    }

    bump(byTask, taskId);
    bump(byAgent, agentId);
    bump(byModel, model);

    if (event.action === 'fix' || event.action === 'qa_run') {
      const cycleKey = `${taskId}:${event.action}`;
      bump(byCycle, cycleKey);
      if (event.action === 'fix') {
        const cycles = fixCyclesByTask.get(taskId) || [];
        cycles.push(usd);
        fixCyclesByTask.set(taskId, cycles);
      }
    }
  }

  const risingTasks = [];
  for (const [taskId, usdSeries] of fixCyclesByTask.entries()) {
    if (usdSeries.length < 2) continue;
    let rising = true;
    for (let i = 1; i < usdSeries.length; i += 1) {
      if (usdSeries[i] <= usdSeries[i - 1]) {
        rising = false;
        break;
      }
    }
    if (rising) risingTasks.push({ taskId, usdSeries });
  }

  return {
    pricing,
    byTask,
    byAgent,
    byCycle,
    byModel,
    projectTotal,
    risingTasks,
    taskCount: tasksData.tasks.length,
  };
}

function formatMapSection(title, map) {
  const lines = [`## ${title}`, ''];
  const entries = [...map.entries()].sort((a, b) => a[0].localeCompare(b[0]));
  if (entries.length === 0) {
    lines.push('_No data_');
    return lines;
  }
  lines.push('| Key | Events | Tokens In | Tokens Out | USD (est) |');
  lines.push('| --- | ---: | ---: | ---: | ---: |');
  for (const [key, val] of entries) {
    lines.push(`| ${key} | ${val.events} | ${val.tokensIn} | ${val.tokensOut} | $${val.usd.toFixed(4)} |`);
  }
  return lines;
}

function renderCostReport(projectRoot) {
  const agg = aggregateCosts(projectRoot);
  const lines = [
    '# Cost Report',
    '',
    '> **Note:** USD values are estimates when explicit `usd` is not logged in activity.',
    '',
    `Pricing version: ${agg.pricing.version}`,
    `Heuristic: ${agg.pricing.heuristic_chars_per_token} chars/token`,
    '',
    '## Project Total',
    '',
    `| Tokens In | Tokens Out | USD (est) |`,
    `| ---: | ---: | ---: |`,
    `| ${agg.projectTotal.tokensIn} | ${agg.projectTotal.tokensOut} | $${agg.projectTotal.usd.toFixed(4)} |`,
    '',
  ];

  lines.push(...formatMapSection('By Task', agg.byTask), '');
  lines.push(...formatMapSection('By Agent', agg.byAgent), '');
  lines.push(...formatMapSection('By Cycle (fix/qa_run)', agg.byCycle), '');
  lines.push(...formatMapSection('By Model', agg.byModel), '');

  lines.push('## Rising Fix-Cycle Cost Flags', '');
  if (agg.risingTasks.length === 0) {
    lines.push('_None_');
  } else {
    for (const item of agg.risingTasks) {
      lines.push(`- **${item.taskId}**: ${item.usdSeries.map((v) => `$${v.toFixed(4)}`).join(' → ')}`);
    }
  }

  lines.push('');
  return lines.join('\n');
}

function runCli(argv) {
  const [projectRoot] = argv;
  if (!projectRoot) {
    console.error('Usage: node tools/cost.js <project_root>');
    process.exit(1);
  }
  console.log(renderCostReport(projectRoot));
}

if (require.main === module) {
  runCli(process.argv.slice(2));
}

module.exports = {
  aggregateCosts,
  renderCostReport,
  estimateTokensFromChars,
  estimateUsd,
  loadPricing,
};
