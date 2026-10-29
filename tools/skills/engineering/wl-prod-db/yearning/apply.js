import { cli, Strategy } from "@jackwener/opencli/registry";
import { openYearning, yearningFetch } from "./api.js";
const REASON = "\u5DE5\u4F5C\u9700\u8981";
cli({
  site: "yearning",
  name: "apply",
  access: "write",
  description: "\u67E5\u8BE2\u65F6\u9650\u4E0D\u5728\u65F6\uFF0C\u7528\u9875\u9762\u539F\u6709\u73AF\u5883\u548C\u5BA1\u6838\u4EBA\u63D0\u4EA4\u8BF4\u660E\u300C\u5DE5\u4F5C\u9700\u8981\u300D\u3002\u65F6\u9650\u8FD8\u5728\u5219\u8DF3\u8FC7\u3002",
  strategy: Strategy.UI,
  browser: true,
  navigateBefore: false,
  defaultFormat: "json",
  defaultWindowMode: "background",
  args: [],
  columns: ["applied", "reason", "description", "idc", "assigned", "status"],
  func: async (page) => {
    await openYearning(page);
    const current = await yearningFetch(page, "PUT", "/api/v2/query/status");
    const status = Number(current.payload?.status);
    if (status === 1) {
      return [{ applied: false, reason: "\u67E5\u8BE2\u65F6\u9650\u4ECD\u6709\u6548", description: "", idc: current.payload?.idc ?? "", assigned: "", status }];
    }
    if (status === 2) {
      return [{ applied: false, reason: "\u7533\u8BF7\u5DF2\u63D0\u4EA4\uFF0C\u6B63\u5728\u7B49\u5F85\u5BA1\u6838\uFF0C\u4E0D\u91CD\u590D\u63D0\u4EA4", description: "", idc: current.payload?.idc ?? "", assigned: "", status }];
    }
    const idc = current.payload?.idc || (await yearningFetch(page, "GET", "/api/v2/fetch/idc")).payload?.[0] || "";
    const source = await yearningFetch(page, "GET", `/api/v2/fetch/source?idc=${encodeURIComponent(idc)}&tp=query`);
    const assigned = source.payload?.assigned?.[0] ?? "";
    if (!idc || !assigned) throw new Error("\u9875\u9762\u6CA1\u6709\u7ED9\u51FA\u73AF\u5883\u6216\u5BA1\u6838\u4EBA\uFF0C\u505C\u6B62\u63D0\u4EA4");
    await yearningFetch(page, "POST", "/api/v2/query/refer", {
      export: 0,
      text: REASON,
      idc,
      assigned
    });
    const after = await yearningFetch(page, "PUT", "/api/v2/query/status");
    return [{
      applied: true,
      reason: "\u5DF2\u63D0\u4EA4\u67E5\u8BE2\u8BF4\u660E",
      description: REASON,
      idc,
      assigned,
      status: Number(after.payload?.status)
    }];
  }
});
