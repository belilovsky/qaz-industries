#!/usr/bin/env node

import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const checkOnly = process.argv.includes("--check");
const packageName = "@sgeo/ui-kit";
const expectedVersion = "4.6.0";
const tarballRelative = "vendor/sgeo-ui-kit-4.6.0.tgz";
const artifactRelative = "avds-package-runtime.css";
const receiptRelative = "data/avds-package-runtime.v1.json";

function sha256(value) {
  return createHash("sha256").update(value).digest("hex");
}

function stableJson(value) {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function assertEqual(actual, expected, message) {
  if (actual !== expected) throw new Error(message);
}

const tarballPath = resolve(root, tarballRelative);
const tarball = readFileSync(tarballPath);
const packageManifest = JSON.parse(execFileSync("tar", ["-xOf", tarballPath, "package/package.json"], { encoding: "utf8" }));
assertEqual(packageManifest.name, packageName, "Unexpected AVDS package name");
assertEqual(packageManifest.version, expectedVersion, "Unexpected AVDS package version");

const source = execFileSync("tar", ["-xOf", tarballPath, "package/src/tokens/variables.css"]);
const header = Buffer.from(
  `/* Generated from ${packageName}@${expectedVersion}/tokens/variables.css. Do not edit. */\n`,
  "utf8",
);
const artifact = Buffer.concat([header, source]);
const receipt = stableJson({
  schema_version: "qaz-industries-avds-package-runtime-v1",
  package: {
    name: packageName,
    version: expectedVersion,
    dependency: tarballRelative,
    tarball_sha256: sha256(tarball),
    export: "@sgeo/ui-kit/tokens/variables.css",
    export_sha256: sha256(source),
  },
  artifact: {
    path: artifactRelative,
    sha256: sha256(artifact),
  },
  runtime: {
    kind: "css-token-export",
    pages: ["index.html", "industry.html", "benchmarks.html", "publication.html"],
    javascript_added: false,
  },
});

const artifactPath = resolve(root, artifactRelative);
const receiptPath = resolve(root, receiptRelative);
if (checkOnly) {
  assertEqual(readFileSync(artifactPath).toString("utf8"), artifact.toString("utf8"), "AVDS runtime CSS is stale");
  assertEqual(readFileSync(receiptPath, "utf8"), receipt, "AVDS package receipt is stale");
  console.log(`AVDS package runtime: OK (${packageName}@${expectedVersion})`);
} else {
  writeFileSync(artifactPath, artifact);
  writeFileSync(receiptPath, receipt, "utf8");
  console.log(`Wrote ${artifactRelative} and ${receiptRelative}`);
}
