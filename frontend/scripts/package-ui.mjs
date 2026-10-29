import { copyFile, mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const root = new URL('../../src/reorderiq/web/', import.meta.url);
await copyFile(new URL('ui/index.html', root), new URL('index.html', root));
await mkdir(new URL('ui/licenses/', root), { recursive: true });
await copyFile(
  new URL('../node_modules/@fontsource/instrument-serif/LICENSE', import.meta.url),
  new URL('ui/licenses/instrument-serif-OFL.txt', root),
);
for (const [name, license] of [
  ['react', 'LICENSE'],
  ['react-dom', 'LICENSE'],
  ['motion', 'LICENSE.md'],
  ['framer-motion', 'LICENSE.md'],
  ['motion-dom', 'LICENSE.md'],
  ['motion-utils', 'LICENSE.md'],
  ['lucide-react', 'LICENSE'],
]) {
  await copyFile(
    new URL(`../node_modules/${name}/${license}`, import.meta.url),
    new URL(`ui/licenses/${name}-LICENSE.txt`, root),
  );
}
console.log(`Packaged React interface into ${fileURLToPath(root)}`);
