#!/usr/bin/env node

/**
 * Knowforge commit message validator.
 *
 * Header format:
 *   <module>\<type>(scope): #<issue> <subject>
 *   <module>\<type>(scope): #<issue>/<subtask> <subject>
 *
 * Example:
 *   cross\feat(chore): #2 bootstrap repo issue workflow
 *
 * Rules:
 * - Header + blank line + non-empty body
 * - Max 100 chars per line
 * - Lowercase module/type/scope/subject
 */

const fs = require('fs');

const COMMIT_FILE = process.argv[2] || '.git/COMMIT_EDITMSG';
const MAX_LINE_LENGTH = 100;

// Adapted modules for Knowforge.
const VALID_MODULES = [
  'all',
  "api",
  'cross',
  'frontend',
  "rag",
];

const VALID_TYPES = [
  'feat',
  'fix',
  'docs',
  'style',
  'refac',
  'perf',
  'test',
  'build',
  'ci',
  'chore',
  'revert',
];

function fail(message, details = []) {
  console.error(`✖ ${message}`);
  for (const line of details) {
    console.error(`  ${line}`);
  }
  process.exit(1);
}

function readCommitMessage(path) {
  try {
    return fs.readFileSync(path, 'utf8').replace(/\r\n/g, '\n').trim();
  } catch (err) {
    fail('Unable to read commit message file', [String(err.message || err)]);
  }
}

function validateLineLength(lines) {
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.length > MAX_LINE_LENGTH) {
      fail(`Line ${i + 1} too long (${line.length} > ${MAX_LINE_LENGTH})`, [line]);
    }
  }
}

function parseHeader(header) {
  if (!header) {
    fail('Commit header cannot be empty');
  }

  const headerMatch = header.match(
    /^([a-z][a-z0-9_-]*)\\([a-z][a-z0-9_-]*)\(([a-z][a-z0-9_-]*)\):\s#(\d+(?:\/\d+)?)\s(.+)$/
  );

  if (!headerMatch) {
    fail('Invalid header format', [
      'Expected: <module>\\<type>(scope): #<issue> <subject>',
      'Example : cross\\feat(chore): #2 bootstrap repo issue workflow',
    ]);
  }

  const [, moduleName, type, scope, issue, subject] = headerMatch;
  return { moduleName, type, scope, issue, subject };
}

function validateHeaderParts({ moduleName, type, scope, subject }) {
  if (!VALID_MODULES.includes(moduleName)) {
    fail(`Invalid module: "${moduleName}"`, [
      `Valid modules: ${VALID_MODULES.join(', ')}`,
    ]);
  }

  if (!VALID_TYPES.includes(type)) {
    fail(`Invalid type: "${type}"`, [
      `Valid types: ${VALID_TYPES.join(', ')}`,
    ]);
  }

  if (!scope.trim()) {
    fail('Scope cannot be empty');
  }

  if (/[A-Z]/.test(subject)) {
    fail('Subject must be lowercase', [`Subject: "${subject}"`]);
  }

  if (!subject.trim()) {
    fail('Subject cannot be empty');
  }
}

function extractBody(lines) {
  const separatorIndex = lines.findIndex((line, idx) => idx > 0 && line.trim() === '');
  if (separatorIndex === -1) {
    fail('Body is required', ['Add one blank line after the header, then your description']);
  }

  const bodyLines = lines.slice(separatorIndex + 1);
  const bodyText = bodyLines.join('\n').trim();

  if (!bodyText) {
    fail('Body cannot be empty');
  }

  return bodyLines;
}

const commitMessage = readCommitMessage(COMMIT_FILE);
const lines = commitMessage.split('\n');
validateLineLength(lines);

const header = lines[0];
const parsed = parseHeader(header);
validateHeaderParts(parsed);

const bodyLines = extractBody(lines);

console.log('✔ Commit message validated successfully');
console.log(`  Module: ${parsed.moduleName}`);
console.log(`  Type: ${parsed.type}`);
console.log(`  Scope: ${parsed.scope}`);
console.log(`  Issue: #${parsed.issue}`);
console.log(`  Subject: ${parsed.subject}`);
console.log(`  Body: ${bodyLines.length} line(s)`);
