// Test the actual template script with a tiny DOM double, no npm dependencies.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const html = fs.readFileSync(path.join(__dirname, '../assets/report.html'), 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
function element(tagName, parentElement = null) {
  return {
    tagName, parentElement, open: false, events: {}, scrolls: 0, focused: false,
    addEventListener(name, fn) { this.events[name] = fn; },
    scrollIntoView() { this.scrolls++; },
    focus() { this.focused = true; },
    querySelector() { return this.summary; },
  };
}
const moduleElement = element('DETAILS');
const body = element('DIV', moduleElement);
const cap = element('DETAILS', body);
cap.summary = element('SUMMARY', cap);
const expand = element('BUTTON');
const collapse = element('BUTTON');
const link = element('A');
link.dataset = {cap: 'cap-demo'};
const tools = {hidden: true};
const ids = {'cap-demo': cap, 'expand-modules': expand, 'collapse-all': collapse};
const window = {events: {}, location: {hash: ''}, addEventListener(name, fn) { this.events[name] = fn; }};
const document = {
  querySelectorAll(selector) {
    return {'details.module': [moduleElement], 'details': [moduleElement, cap], 'a[data-cap]': [link]}[selector];
  },
  querySelector() { return tools; },
  getElementById(id) { return ids[id] || null; },
};
vm.runInNewContext(script, {document, window});
assert.equal(tools.hidden, false);
expand.events.click();
assert.equal(moduleElement.open, true);
assert.equal(cap.open, false, 'expand modules must not expand all capabilities');
collapse.events.click();
assert.equal(moduleElement.open, false);
let prevented = false;
link.events.click({preventDefault() { prevented = true; }});
assert.equal(prevented, true);
assert.equal(moduleElement.open, true);
assert.equal(cap.open, true);
assert.equal(cap.scrolls, 1);
assert.equal(cap.summary.focused, true);
assert.equal(window.location.hash, 'cap-demo');
collapse.events.click();
assert.equal(cap.open, false);
window.location.hash = '#cap-demo';
window.events.hashchange();
assert.equal(moduleElement.open, true);
assert.equal(cap.open, true);
window.location.hash = '#cap-does-not-exist';
window.events.hashchange(); // unknown hash must not throw
moduleElement.open = false;
cap.open = true;
window.events.beforeprint();
assert.equal(moduleElement.open, true);
assert.equal(cap.open, true);
window.events.beforeprint(); // must preserve original snapshot
window.events.afterprint();
assert.equal(moduleElement.open, false);
assert.equal(cap.open, true);
window.events.afterprint(); // duplicate completion must not corrupt state
assert.equal(moduleElement.open, false);
assert.equal(cap.open, true);
// Fresh page with an initial deep link must reveal both levels.
moduleElement.open = false;
cap.open = false;
window.location.hash = '#cap-demo';
vm.runInNewContext(script, {document, window});
assert.equal(moduleElement.open, true);
assert.equal(cap.open, true);
console.log('PASS: expand/collapse, reveal/keyboard focus, initial/hash navigation, print restore/reentrancy');
