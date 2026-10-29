const fs = require('node:fs');
// No titles, errors, attachments, paths, identity or network data in this summary.
module.exports = class SummaryReporter {
  onBegin(_config, suite) { this.total = suite.allTests().length; this.finished = 0; }
  onTestEnd(_test, result) {
    this.finished++;
    if (/^(?:Error: )?STATE_MISSING$/.test(result.error?.message || '')) this.failureCode = 'STATE_MISSING';
  }
  onEnd(result) {
    fs.writeFileSync(process.env.PLAYWRIGHT_AUTH_SUMMARY, JSON.stringify({
      testsDiscovered: this.total || 0, testsFinished: this.finished || 0,
      passed: result.status === 'passed', failureCode: this.failureCode || null,
    }), { mode: 0o600 });
  }
};
