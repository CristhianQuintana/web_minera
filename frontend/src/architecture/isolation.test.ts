import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import { describe, expect, it } from "vitest";

const SRC = join(__dirname, "..");

function walk(dir: string): string[] {
  const out: string[] = [];
  for (const name of readdirSync(dir)) {
    const full = join(dir, name);
    if (statSync(full).isDirectory()) {
      if (name === "node_modules" || name === ".next") continue;
      out.push(...walk(full));
    } else if (/\.(ts|tsx)$/.test(name)) {
      out.push(full);
    }
  }
  return out;
}

function importsOf(source: string): string[] {
  const matches = source.matchAll(/from\s+["']([^"']+)["']/g);
  return [...matches].map((m) => m[1]);
}

describe("arquitectura hexagonal frontend", () => {
  it("domain no importa adapters, composition ni next/react", () => {
    const files = walk(join(SRC, "domain"));
    const violations: string[] = [];
    for (const file of files) {
      for (const imp of importsOf(readFileSync(file, "utf8"))) {
        if (
          imp.startsWith("@/adapters") ||
          imp.startsWith("@/composition") ||
          imp.startsWith("@/infrastructure") ||
          imp.startsWith("next") ||
          imp === "react" ||
          imp.startsWith("react/")
        ) {
          violations.push(`${relative(SRC, file)} → ${imp}`);
        }
      }
    }
    expect(violations).toEqual([]);
  });

  it("application no importa adapters ni next", () => {
    const files = walk(join(SRC, "application"));
    const violations: string[] = [];
    for (const file of files) {
      for (const imp of importsOf(readFileSync(file, "utf8"))) {
        if (imp.startsWith("@/adapters") || imp.startsWith("next") || imp.includes("platform-adapter")) {
          violations.push(`${relative(SRC, file)} → ${imp}`);
        }
      }
    }
    expect(violations).toEqual([]);
  });

  it("ports no importan adapters", () => {
    const files = walk(join(SRC, "ports"));
    const violations: string[] = [];
    for (const file of files) {
      for (const imp of importsOf(readFileSync(file, "utf8"))) {
        if (imp.startsWith("@/adapters") || imp.startsWith("@/composition")) {
          violations.push(`${relative(SRC, file)} → ${imp}`);
        }
      }
    }
    expect(violations).toEqual([]);
  });

  it("composition es el único lugar que cablea platformAdapter", () => {
    const offenders: string[] = [];
    for (const file of walk(SRC)) {
      const rel = relative(SRC, file).replace(/\\/g, "/");
      if (rel === "composition/container.ts") continue;
      if (rel === "adapters/outbound/api/platform-adapter.ts") continue;
      if (rel.endsWith(".test.ts") || rel.endsWith(".test.tsx")) continue;
      const text = readFileSync(file, "utf8");
      if (text.includes("platformAdapter") || text.includes("@/adapters/outbound/api/platform-adapter")) {
        offenders.push(rel);
      }
    }
    expect(offenders).toEqual([]);
  });
});
