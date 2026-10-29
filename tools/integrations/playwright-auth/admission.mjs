import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { fail } from './store.mjs';
const fixture = fileURLToPath(new URL('./fixture.mjs', import.meta.url));

// Deliberately narrow migration contract, not a JS parser or a hostile-code sandbox.
// A supported spec begins with the unaliased shared test import and has no helper
// imports/re-exports/dynamic loading. Unsupported forms fail closed.
export function admitSpec(source, spec) {
  const first = /^\s*import\s*\{\s*test\s*(?:,\s*expect\s*)?\}\s*from\s*(['"])([^'"\r\n]+)\1\s*;/.exec(source);
  if (!first || path.resolve(path.dirname(spec), first[2]) !== fixture) fail('FIXTURE_IMPORT_REQUIRED');
  const body = source.slice(first[0].length);
  // Conservative lexical restrictions intentionally reject some harmless strings
  // or comments; use the documented simple form instead of guessing semantics.
  if (/\b(?:import|export|require)\b|\b(?:const|let|var|function|class)\s+test\b|\btest\s*=/.test(body)) fail('UNSUPPORTED_SPEC_FORM');
  if (!/^\s*test\s*\(/m.test(body)) fail('UNSUPPORTED_SPEC_FORM');
  return true;
}
