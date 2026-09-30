'use strict';

// Two bundles: the extension host (Node) and the webview UI (browser).
const esbuild = require('esbuild');

const watch = process.argv.includes('--watch');

const extension = {
  entryPoints: ['src/extension/extension.ts'],
  bundle: true,
  outfile: 'dist/extension.js',
  external: ['vscode'],
  format: 'cjs',
  platform: 'node',
  target: 'node18',
  sourcemap: true,
  minify: false,
};

const webview = {
  entryPoints: ['src/webview/main.ts'],
  bundle: true,
  outfile: 'dist/webview.js',
  format: 'iife',
  platform: 'browser',
  target: 'es2020',
  sourcemap: true,
  minify: !watch,
  loader: { '.css': 'css' },
};

async function main() {
  if (watch) {
    const ctxs = await Promise.all([esbuild.context(extension), esbuild.context(webview)]);
    await Promise.all(ctxs.map((c) => c.watch()));
    console.log('[amir_md] watching...');
  } else {
    await Promise.all([esbuild.build(extension), esbuild.build(webview)]);
    console.log('[amir_md] built dist/extension.js and dist/webview.js');
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
