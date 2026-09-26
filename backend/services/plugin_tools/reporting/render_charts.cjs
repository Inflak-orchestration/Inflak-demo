const fs = require("node:fs");
const vega = require("vega");
const vegaLite = require("vega-lite");

async function main() {
  const specifications = JSON.parse(fs.readFileSync(0, "utf8"));
  const results = [];
  for (const specification of specifications) {
    let view;
    try {
      const compiled = vegaLite.compile(specification).spec;
      const loader = vega.loader();
      loader.load = async () => { throw new Error("External resources are disabled"); };
      loader.sanitize = async () => { throw new Error("External resources are disabled"); };
      view = new vega.View(vega.parse(compiled), { renderer: "none", loader });
      await view.runAsync();
      results.push({ svg: await view.toSVG() });
    } catch (error) {
      results.push({ error: "Invalid or unsupported Vega-Lite specification" });
    } finally {
      if (view) view.finalize();
    }
  }
  process.stdout.write(JSON.stringify(results));
}

main().catch(() => { process.exitCode = 1; });