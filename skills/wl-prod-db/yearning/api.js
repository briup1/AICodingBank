const ORIGIN = "http://yearning.hgj.net";
async function openYearning(page) {
  await page.goto(`${ORIGIN}/#/query/order`, { waitUntil: "load", settleMs: 800 });
}
async function yearningFetch(page, method, path, body) {
  const result = await page.evaluate(
    async (method2, path2, body2) => {
      const jwt = localStorage.getItem("jwt");
      if (!jwt) return { error: "\u672A\u767B\u5F55 Yearning\uFF0C\u5148\u5728 Chrome \u91CC\u767B\u5F55\u540E\u518D\u8BD5" };
      const headers = { Authorization: jwt };
      const init = { method: method2, headers };
      if (body2 !== null && body2 !== void 0) {
        headers["Content-Type"] = "application/json";
        init.body = JSON.stringify(body2);
      }
      const response = await fetch(path2, init);
      const text = await response.text();
      try {
        return { http: response.status, data: JSON.parse(text) };
      } catch {
        return { http: response.status, data: { code: response.status, text, payload: null } };
      }
    },
    method,
    path,
    body ?? null
  );
  if (result && typeof result === "object" && "error" in result && result.error) {
    throw new Error(String(result.error));
  }
  const data = result.data;
  if (!data || typeof data !== "object") throw new Error(`Yearning \u8FD4\u56DE\u65E0\u6CD5\u89E3\u6790: ${path}`);
  if (data.code !== void 0 && data.code !== 1200) {
    throw new Error(data.text || `Yearning ${path} \u5931\u8D25\uFF0Ccode=${data.code}`);
  }
  return data;
}
export {
  openYearning,
  yearningFetch
};
