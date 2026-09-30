// Package the real Workings application for review through a shared local file.
import { readFile, mkdir, writeFile } from "node:fs/promises";
import { resolve, join } from "node:path";
import { pathToFileURL } from "node:url";
import { createHash } from "node:crypto";

const [sourceArg, outputArg, mode = "compare"] = process.argv.slice(2);
if (!sourceArg || !outputArg || !["baseline", "history", "compare"].includes(mode)) {
  throw new Error("Usage: node build.mjs <Workings checkout> <new output folder> [baseline|history|compare]");
}
const source = resolve(sourceArg);
const output = resolve(outputArg);
await mkdir(output, { recursive: false });
const { build } = await import(pathToFileURL(join(source, "node_modules/vite/dist/node/index.js")));
const result = await build({
  root: source,
  configFile: join(source, "vite.config.ts"),
  base: "./",
  define: { "import.meta.env.VITE_RUN_COMPARISON": JSON.stringify(mode) },
  build: {
    write: false, assetsInlineLimit: 100000000, cssCodeSplit: false,
    modulePreload: false,
    rollupOptions: { output: { inlineDynamicImports: true } },
  },
});
const items = result.output;
const scripts = items.filter(item => item.type === "chunk");
if (scripts.length !== 1) throw new Error("The review build must contain one script.");
const js = scripts[0].code.replace(/<\/script/gi, "<\\/script");
const css = items.filter(item => item.type === "asset" && item.fileName.endsWith(".css"))
  .map(item => String(item.source)).join("\n");
const hash = value => createHash("sha256").update(value).digest("base64");
const policy = `default-src 'none'; script-src 'sha256-${hash(js)}'; style-src 'unsafe-inline'; font-src data:; img-src data: blob:; base-uri 'none'; form-action 'none'`;
const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="Content-Security-Policy" content="${policy}"><title>Workings</title><style>${css}</style></head><body><div id="root"></div><script type="module">${js}</script></body></html>`;
await writeFile(join(output, "index.html"), html);
await writeFile(join(output, "tool-using-agent.json"), await readFile(join(source, "src/content/lessons/tool-using-agent.json")));
await writeFile(join(output, "retry-tools.json"), await readFile(join(source, "src/content/lessons/retry-tools.json")));
await writeFile(join(output, "build.json"), JSON.stringify({ mode, html_sha256: createHash("sha256").update(html).digest("hex"), bytes: Buffer.byteLength(html) }, null, 2) + "\n");
console.log(`Built ${mode}: ${join(output, "index.html")}`);
