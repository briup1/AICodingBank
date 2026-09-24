const ORIGIN = "http://archery.hgj.net";
async function openArchery(page) {
  await page.goto(`${ORIGIN}/sqlquery/`, { waitUntil: "load", settleMs: 800 });
}
async function archeryFetch(page, path, params) {
  const result = await page.evaluate(async (path2, params2) => {
    const cookie = document.cookie.split(";").map((item) => item.trim()).find((item) => item.startsWith("csrftoken="));
    if (!cookie) return { error: "\u672A\u767B\u5F55 Archery\uFF0C\u5148\u5728 Chrome \u91CC\u767B\u5F55\u540E\u518D\u8BD5" };
    const token = decodeURIComponent(cookie.slice("csrftoken=".length));
    const body = new URLSearchParams(params2);
    const response = await fetch(path2, {
      method: "POST",
      headers: {
        "X-CSRFToken": token,
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
      },
      body
    });
    const text = await response.text();
    try {
      return { http: response.status, data: JSON.parse(text) };
    } catch {
      return { http: response.status, data: { status: response.status, msg: text } };
    }
  }, path, params);
  if (result && typeof result === "object" && "error" in result && result.error) {
    throw new Error(String(result.error));
  }
  const data = result.data;
  if (!data || data.status !== 0) {
    throw new Error(data?.msg || "Archery \u67E5\u8BE2\u5931\u8D25");
  }
  return data;
}
async function archeryGet(page, path, params) {
  const query = new URLSearchParams(params).toString();
  const result = await page.evaluate(async (url) => {
    const response = await fetch(url);
    const text = await response.text();
    try {
      return JSON.parse(text);
    } catch {
      return { status: response.status, msg: text };
    }
  }, `${path}?${query}`);
  if (!result || result.status !== 0) {
    throw new Error(result?.msg || "Archery \u8BFB\u53D6\u5931\u8D25");
  }
  return result;
}
export {
  archeryFetch,
  archeryGet,
  openArchery
};
