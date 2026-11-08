/**
 * Auditoría de accesibilidad WCAG 2.1 A/AA — WEB_MINERA
 * Playwright + @axe-core/playwright
 *
 * Uso:
 *   $env:BASE_URL="http://127.0.0.1:3000"
 *   npm run audit:accessibility
 *
 * Sesión autenticada (opcional, no versionar):
 *   $env:PLAYWRIGHT_STORAGE_STATE="playwright/.auth/user.json"
 *
 * Aviso: cero violaciones automáticas NO declara cumplimiento WCAG 2.1 AA.
 */

import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import fs from 'node:fs';
import path from 'node:path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, '..');
const FRONTEND_ROOT = path.join(REPO_ROOT, 'frontend');

// Resolver dependencias desde frontend/ (Playwright ya instalado allí).
const requireFrontend = createRequire(path.join(FRONTEND_ROOT, 'package.json'));
const { chromium } = requireFrontend('playwright');
const AxeBuilderModule = requireFrontend('@axe-core/playwright');
const AxeBuilder = AxeBuilderModule.default ?? AxeBuilderModule;

const BASE_URL = process.env.BASE_URL;

/** Rutas reales del App Router de WEB_MINERA. Sobrescribir con AUDIT_PAGES. */
const DEFAULT_PAGES = [
  '/',
  '/login',
  '/forgot-password',
  '/activate-account',
  '/dashboard',
  '/lots',
  '/custody',
  '/transport',
  '/receptions',
  '/weighings',
  '/alerts',
  '/mass-balance',
  '/audit',
  '/users',
  '/settings',
  '/profile',
  '/ml',
].join(',');

const PAGES = (process.env.AUDIT_PAGES || DEFAULT_PAGES)
  .split(',')
  .map((page) => page.trim())
  .filter(Boolean);

const OUTPUT_DIR = path.join(REPO_ROOT, 'reports', 'accessibility');

if (!BASE_URL) {
  throw new Error(
    'Debe configurar la variable BASE_URL (ej. http://127.0.0.1:3000).',
  );
}

fs.mkdirSync(OUTPUT_DIR, { recursive: true });

const browser = await chromium.launch({
  headless: true,
});

function resolveStorageStatePath(raw) {
  if (!raw) return undefined;
  if (path.isAbsolute(raw)) return raw;
  return path.join(REPO_ROOT, raw);
}

const storageStatePath = resolveStorageStatePath(process.env.PLAYWRIGHT_STORAGE_STATE);

const context = await browser.newContext({
  viewport: {
    width: 1366,
    height: 768,
  },
  ...(storageStatePath && fs.existsSync(storageStatePath)
    ? { storageState: storageStatePath }
    : {}),
});

const results = [];

try {
  for (const route of PAGES) {
    const url = new URL(route, BASE_URL).toString();

    console.log(`\nAnalizando: ${url}`);

    const page = await context.newPage();

    try {
      const response = await page.goto(url, {
        waitUntil: 'domcontentloaded',
        timeout: 60000,
      });

      await page.locator('body').waitFor();

      // Permitir que termine el renderizado inicial.
      await page.waitForTimeout(1000);

      const accessibility = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
        .analyze();

      const impactCounts = { critical: 0, serious: 0, moderate: 0, minor: 0 };
      for (const v of accessibility.violations) {
        const key = v.impact || 'minor';
        if (impactCounts[key] !== undefined) impactCounts[key] += 1;
      }

      const result = {
        url,
        finalUrl: page.url(),
        statusCode: response?.status() ?? null,
        scannedAt: new Date().toISOString(),
        summary: {
          violations: accessibility.violations.length,
          passes: accessibility.passes.length,
          incomplete: accessibility.incomplete.length,
          inapplicable: accessibility.inapplicable.length,
          byImpact: impactCounts,
        },
        violations: accessibility.violations,
        incomplete: accessibility.incomplete,
        passes: accessibility.passes.map((p) => ({
          id: p.id,
          impact: p.impact,
          tags: p.tags,
          description: p.description,
          help: p.help,
        })),
      };

      results.push(result);

      console.log(
        `Violaciones: ${result.summary.violations} | ` +
          `Aprobadas: ${result.summary.passes} | ` +
          `Revisión manual: ${result.summary.incomplete} | ` +
          `impactos: c=${impactCounts.critical} s=${impactCounts.serious} m=${impactCounts.moderate} n=${impactCounts.minor}`,
      );
    } catch (error) {
      results.push({
        url,
        error: error.message,
      });

      console.error(`Error al analizar ${url}:`, error.message);
    } finally {
      await page.close();
    }
  }
} finally {
  await browser.close();
}

const impactTotals = { critical: 0, serious: 0, moderate: 0, minor: 0 };
for (const item of results) {
  const bi = item.summary?.byImpact;
  if (!bi) continue;
  for (const k of Object.keys(impactTotals)) {
    impactTotals[k] += bi[k] || 0;
  }
}

const report = {
  project: 'WEB_MINERA',
  standard: 'WCAG 2.1 AA',
  tool: 'Playwright + axe-core',
  disclaimer:
    'Cero violaciones automáticas NO declara cumplimiento WCAG 2.1 AA. Se requiere validación manual complementaria (teclado, foco, lector de pantalla, contraste, modales).',
  generatedAt: new Date().toISOString(),
  baseUrl: BASE_URL,
  storageStateUsed: Boolean(
    storageStatePath && fs.existsSync(storageStatePath),
  ),
  storageStatePath: storageStatePath && fs.existsSync(storageStatePath)
    ? storageStatePath
    : null,
  pagesAnalyzed: results.length,
  totalViolations: results.reduce(
    (sum, item) => sum + (item.summary?.violations ?? 0),
    0,
  ),
  totalPasses: results.reduce(
    (sum, item) => sum + (item.summary?.passes ?? 0),
    0,
  ),
  totalIncomplete: results.reduce(
    (sum, item) => sum + (item.summary?.incomplete ?? 0),
    0,
  ),
  impactTotals,
  results,
};

const stamp = report.generatedAt.replace(/[:.]/g, '-');
const jsonPath = path.join(OUTPUT_DIR, 'accessibility-report.json');
const htmlPath = path.join(OUTPUT_DIR, 'accessibility-report.html');
const jsonHistoryPath = path.join(
  OUTPUT_DIR,
  `accessibility-report-${stamp}.json`,
);
const htmlHistoryPath = path.join(
  OUTPUT_DIR,
  `accessibility-report-${stamp}.html`,
);

fs.writeFileSync(jsonPath, JSON.stringify(report, null, 2));
fs.writeFileSync(jsonHistoryPath, JSON.stringify(report, null, 2));

const escapeHtml = (value) =>
  String(value).replace(
    /[&<>"']/g,
    (char) =>
      ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
      })[char],
  );

const impactBadge = (impact) => {
  const colors = {
    critical: '#9b1c1c',
    serious: '#b45309',
    moderate: '#a16207',
    minor: '#475569',
  };
  const color = colors[impact] || '#334155';
  return `<span style="display:inline-block;padding:2px 8px;border-radius:4px;background:${color};color:#fff;font-size:12px;">${escapeHtml(impact || 'n/d')}</span>`;
};

const renderViolation = (v) => {
  const nodes = (v.nodes || [])
    .map((node) => {
      const targets = (node.target || []).map(escapeHtml).join(', ');
      return `<tr>
<td><code>${targets}</code></td>
<td><pre>${escapeHtml(node.html || '')}</pre></td>
<td>${escapeHtml(node.failureSummary || node.impact || '')}</td>
</tr>`;
    })
    .join('');

  const tags = (v.tags || []).map(escapeHtml).join(', ');
  const helpUrl = v.helpUrl
    ? `<a href="${escapeHtml(v.helpUrl)}" target="_blank" rel="noopener">Recomendación / documentación axe</a>`
    : '';

  return `<article style="margin:16px 0;padding:12px;border:1px solid #e2e8f0;border-radius:8px;">
<h5>${escapeHtml(v.id)} — ${escapeHtml(v.help || v.description || '')} ${impactBadge(v.impact)}</h5>
<p>${escapeHtml(v.description || '')}</p>
<p><strong>Impacto:</strong> ${impactBadge(v.impact)}</p>
<p><strong>WCAG / tags:</strong> ${tags}</p>
<p><strong>Corrección sugerida:</strong> ${escapeHtml(v.help || '')}. ${helpUrl}</p>
<table>
<thead><tr><th>Selector</th><th>HTML afectado</th><th>Detalle</th></tr></thead>
<tbody>${nodes || '<tr><td colspan="3">Sin nodos</td></tr>'}</tbody>
</table>
</article>`;
};

const renderIncomplete = (items) => {
  if (!items?.length) return '<p>Ninguno.</p>';
  return `<ul>${items
    .map(
      (i) =>
        `<li><strong>${escapeHtml(i.id)}</strong>: ${escapeHtml(i.help || i.description || '')} ${impactBadge(i.impact)}
         <br/><small>Tags: ${escapeHtml((i.tags || []).join(', '))}</small></li>`,
    )
    .join('')}</ul>`;
};

const html = `<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Auditoría de accesibilidad - WEB_MINERA</title>
<style>
body { font-family: Arial, sans-serif; margin: 32px; color: #222; line-height: 1.45; }
h1, h2, h3, h4, h5 { color: #17365d; }
table { border-collapse: collapse; width: 100%; margin: 12px 0 20px; }
th, td { border: 1px solid #ddd; padding: 10px; text-align: left; vertical-align: top; }
th { background: #edf2f7; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; margin: 0; font-size: 12px; }
.note { background: #fff7ed; border: 1px solid #fdba74; padding: 12px; border-radius: 8px; }
</style>
</head>
<body>
<h1>Reporte de accesibilidad – WEB_MINERA</h1>
<p>Estándar evaluado: WCAG 2.1 A y AA</p>
<p>Herramientas: Playwright + axe-core</p>
<p>Fecha: ${escapeHtml(report.generatedAt)}</p>
<p>BASE_URL: ${escapeHtml(report.baseUrl)}</p>
<p>Sesión autenticada: ${report.storageStateUsed ? 'Sí' : 'No'}</p>
<p class="note"><strong>Aviso:</strong> ${escapeHtml(report.disclaimer)}</p>
<h2>Resumen general</h2>
<table>
<tr><th>Métrica</th><th>Resultado</th></tr>
<tr><td>Páginas analizadas</td><td>${report.pagesAnalyzed}</td></tr>
<tr><td>Violaciones (reglas fallidas)</td><td>${report.totalViolations}</td></tr>
<tr><td>Reglas aprobadas</td><td>${report.totalPasses}</td></tr>
<tr><td>Revisión manual (incomplete)</td><td>${report.totalIncomplete}</td></tr>
<tr><td>Impacto critical</td><td>${impactTotals.critical}</td></tr>
<tr><td>Impacto serious</td><td>${impactTotals.serious}</td></tr>
<tr><td>Impacto moderate</td><td>${impactTotals.moderate}</td></tr>
<tr><td>Impacto minor</td><td>${impactTotals.minor}</td></tr>
</table>
<h2>Resultados por página</h2>
${results
  .map((item) => {
    if (item.error) {
      return `<section>
<h3>${escapeHtml(item.url)}</h3>
<p>Error: ${escapeHtml(item.error)}</p>
</section><hr>`;
    }
    const violationsHtml =
      (item.violations || []).map(renderViolation).join('') ||
      '<p>Sin violaciones automáticas en esta página.</p>';
    return `<section>
<h3>${escapeHtml(item.url)}</h3>
<p>URL final: ${escapeHtml(item.finalUrl || item.url)}</p>
<p>HTTP: ${escapeHtml(String(item.statusCode))} · Escaneo: ${escapeHtml(item.scannedAt)}</p>
<p>Violaciones: ${item.summary.violations} |
   Aprobadas: ${item.summary.passes} |
   Revisión manual: ${item.summary.incomplete}</p>
<p>Por impacto — critical: ${item.summary.byImpact.critical},
 serious: ${item.summary.byImpact.serious},
 moderate: ${item.summary.byImpact.moderate},
 minor: ${item.summary.byImpact.minor}</p>
<h4>Hallazgos (violaciones)</h4>
${violationsHtml}
<h4>Revisión manual (incomplete)</h4>
${renderIncomplete(item.incomplete)}
</section>
<hr>`;
  })
  .join('')}
</body>
</html>
`;

fs.writeFileSync(htmlPath, html);
fs.writeFileSync(htmlHistoryPath, html);

// Registro tabular de hallazgos para el informe académico
const findings = [];
for (const item of results) {
  if (item.error || !item.violations) continue;
  for (const v of item.violations) {
    for (const node of v.nodes || [{ target: [], html: '', failureSummary: '' }]) {
      findings.push({
        url: item.url,
        ruleId: v.id,
        impact: v.impact,
        wcagTags: (v.tags || []).filter((t) => /wcag/i.test(t)),
        description: v.description,
        help: v.help,
        helpUrl: v.helpUrl,
        selector: (node.target || []).join(' | '),
        html: node.html || '',
        failureSummary: node.failureSummary || '',
      });
    }
  }
}
fs.writeFileSync(
  path.join(OUTPUT_DIR, 'findings-register.json'),
  JSON.stringify(
    {
      generatedAt: report.generatedAt,
      totalFindingNodes: findings.length,
      disclaimer: report.disclaimer,
      findings,
    },
    null,
    2,
  ),
);

const sep = '='.repeat(72);
const thin = '-'.repeat(72);

console.log(`\n${sep}`);
console.log('RESULTADOS FINALES — Auditoría de accesibilidad WEB_MINERA');
console.log(sep);
console.log(`Proyecto:     ${report.project}`);
console.log(`Estándar:     ${report.standard}`);
console.log(`Herramienta:  ${report.tool}`);
console.log(`Fecha:        ${report.generatedAt}`);
console.log(`BASE_URL:     ${report.baseUrl}`);
console.log(
  `Sesión auth:  ${report.storageStateUsed ? 'Sí' : 'No'}`,
);
console.log(thin);
console.log('RESUMEN GENERAL');
console.log(thin);
console.log(`  Páginas analizadas:     ${report.pagesAnalyzed}`);
console.log(`  Violaciones:            ${report.totalViolations}`);
console.log(`  Reglas aprobadas:       ${report.totalPasses}`);
console.log(`  Revisión manual:        ${report.totalIncomplete}`);
console.log(
  `  Impactos:               critical=${impactTotals.critical} serious=${impactTotals.serious} moderate=${impactTotals.moderate} minor=${impactTotals.minor}`,
);
console.log(thin);
console.log('RESULTADOS POR PÁGINA');
console.log(thin);
for (const item of results) {
  if (item.error) {
    console.log(`  ✗ ${item.url}`);
    console.log(`      ERROR: ${item.error}`);
    continue;
  }
  const mark = item.summary.violations > 0 ? '✗' : '✓';
  console.log(`  ${mark} ${item.url}`);
  console.log(
    `      final=${item.finalUrl || item.url}  HTTP=${item.statusCode}`,
  );
  console.log(
    `      violaciones=${item.summary.violations}  aprobadas=${item.summary.passes}  revisión_manual=${item.summary.incomplete}`,
  );
  console.log(
    `      impacto: c=${item.summary.byImpact.critical} s=${item.summary.byImpact.serious} m=${item.summary.byImpact.moderate} n=${item.summary.byImpact.minor}`,
  );
}

if (findings.length > 0) {
  console.log(thin);
  console.log(`DETALLE DE VIOLACIONES (${findings.length} nodo(s) afectado(s))`);
  console.log(thin);
  findings.forEach((f, i) => {
    console.log(`  [${i + 1}] ${f.url}`);
    console.log(`      Regla:      ${f.ruleId}  |  Impacto: ${f.impact}`);
    console.log(
      `      WCAG/tags:  ${(f.wcagTags || []).join(', ') || 'n/d'}`,
    );
    console.log(`      Descripción: ${f.description}`);
    console.log(`      Ayuda:       ${f.help}`);
    console.log(`      Selector:    ${f.selector || '(sin selector)'}`);
    console.log(
      `      HTML:        ${(f.html || '').slice(0, 160)}${(f.html || '').length > 160 ? '…' : ''}`,
    );
    if (f.failureSummary) {
      console.log(`      Detalle:     ${f.failureSummary.replace(/\n/g, ' | ')}`);
    }
    if (f.helpUrl) console.log(`      Doc:        ${f.helpUrl}`);
    console.log('');
  });
} else {
  console.log(thin);
  console.log('DETALLE DE VIOLACIONES: ninguna detectada por axe-core.');
}

const incompleteItems = [];
for (const item of results) {
  if (!item.incomplete?.length) continue;
  for (const inc of item.incomplete) {
    incompleteItems.push({
      url: item.url,
      id: inc.id,
      impact: inc.impact,
      help: inc.help || inc.description,
      tags: (inc.tags || []).join(', '),
    });
  }
}
if (incompleteItems.length > 0) {
  console.log(thin);
  console.log(`REVISIÓN MANUAL / INCOMPLETE (${incompleteItems.length})`);
  console.log(thin);
  for (const inc of incompleteItems) {
    console.log(`  • ${inc.url} — ${inc.id} (${inc.impact || 'n/d'})`);
    console.log(`      ${inc.help}`);
    if (inc.tags) console.log(`      tags: ${inc.tags}`);
  }
}

console.log(thin);
console.log('DICTAMEN AUTOMÁTICO');
console.log(thin);
if (results.some((r) => r.error)) {
  console.log('  Estado: ERRORES DE EJECUCIÓN (algunas páginas no se analizaron).');
} else if (report.totalViolations > 0) {
  console.log(
    `  Estado: CON HALLAZGOS — ${report.totalViolations} violación(es) axe en WCAG 2.1 A/AA.`,
  );
} else {
  console.log(
    '  Estado: SIN VIOLACIONES AUTOMÁTICAS en las páginas evaluadas.',
  );
}
console.log(
  '  Aviso: cero violaciones automáticas NO declara cumplimiento WCAG 2.1 AA.',
);
console.log(
  '  Complementar con pruebas manuales (teclado, foco, lector de pantalla, contraste, modales).',
);
console.log(thin);
console.log('ARCHIVOS GENERADOS (referencia)');
console.log(`  JSON:      ${jsonPath}`);
console.log(`  HTML:      ${htmlPath}`);
console.log(`  Histórico: ${jsonHistoryPath}`);
console.log(
  `  Hallazgos: ${path.join(OUTPUT_DIR, 'findings-register.json')}`,
);
console.log(`${sep}\n`);

if (results.some((r) => r.error)) {
  process.exitCode = 2;
} else if (report.totalViolations > 0) {
  process.exitCode = 1;
}
