'use strict';

const esbuild = require('esbuild');

const watch = process.argv.includes('--watch');

const ctx = {
  entryPoints: ['src/extension.ts'],
  bundle: true,
  outfile: 'dist/extension.js',
  external: ['vscode'],
  format: 'cjs',
  platform: 'node',
  target: 'node18',
  sourcemap: true,
  minify: false,
};

async function main() {
  if (watch) {
    const context = await esbuild.context(ctx);
    await context.watch();
    console.log('[amir] watching…');
  } else {
    await esbuild.build(ctx);
    console.log('[amir] built dist/extension.js');
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
