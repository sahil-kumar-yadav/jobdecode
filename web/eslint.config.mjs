import { dirname } from 'path';
import { fileURLToPath } from 'url';
import { FlatCompat } from '@eslint/eslintrc';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Next.js provides its own recommended ESLint config.
// This file exists to keep `next lint` working if ESLint is used.
export default [
  {
    ignores: ['dist', 'node_modules', '.next'],
  },
];

