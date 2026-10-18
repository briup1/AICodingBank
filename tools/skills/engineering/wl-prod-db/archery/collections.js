import { cli, Strategy } from "@jackwener/opencli/registry";
import { assertDatabase, assertInstance } from "./guard.js";
import { archeryGet, openArchery } from "./api.js";
cli({
  site: "archery",
  name: "collections",
  access: "read",
  description: "\u5217\u51FA\u4E00\u4E2A\u751F\u4EA7 Mongo \u5E93\u4E0B\u7684\u96C6\u5408\u3002",
  strategy: Strategy.UI,
  browser: true,
  navigateBefore: false,
  defaultFormat: "json",
  defaultWindowMode: "background",
  args: [
    { name: "instance", required: true, help: "\u5B9E\u4F8B\u540D\uFF0C\u5FC5\u987B prd-mongo \u5F00\u5934" },
    { name: "database", required: true, help: "\u6570\u636E\u5E93\u540D" }
  ],
  columns: ["name"],
  validateArgs: (kwargs) => {
    kwargs.instance = assertInstance(String(kwargs.instance ?? ""));
    kwargs.database = assertDatabase(String(kwargs.database ?? ""));
  },
  func: async (page, kwargs) => {
    await openArchery(page);
    const result = await archeryGet(page, "/instance/instance_resource/", {
      instance_name: String(kwargs.instance),
      db_name: String(kwargs.database),
      resource_type: "table"
    });
    const names = Array.isArray(result.data) ? result.data : [];
    return names.map((name) => ({ name: String(name) }));
  }
});
