/**
 * Dependency Cruiser — WEB_MINERA Frontend (Next.js / TypeScript hexagonal)
 *
 * Estructura real bajo frontend/src/:
 *   domain, application, ports, adapters, composition, infrastructure,
 *   presentation, shared, config, app (Next.js App Router)
 *
 * Alias: @/* → ./src/* (tsconfig paths).
 * No se ocultan violaciones conocidas (p. ej. pages → adapters/http-client).
 */

/** @type {import('dependency-cruiser').IConfiguration} */
module.exports = {
  forbidden: [
    {
      name: "domain-no-ui-or-outer-layers",
      comment:
        "El dominio no debe importar React, Next.js, adaptadores, composition, infrastructure ni presentation.",
      severity: "error",
      from: { path: "(^|/|\\\\)domain(/|\\\\|$)" },
      to: {
        path: "(^react(-dom)?(/|$)|(^|/)next(/|$)|(^|/|\\\\)(adapters|composition|infrastructure|presentation|app)(/|\\\\|$))",
        pathNot: "(^|/|\\\\)domain(/|\\\\|$)",
      },
    },
    {
      name: "domain-no-node-modules-ui",
      comment: "Dominio sin dependencias de paquetes UI/framework.",
      severity: "error",
      from: { path: "(^|/|\\\\)src(/|\\\\)domain(/|\\\\|$)" },
      to: {
        dependencyTypes: ["npm", "npm-dev", "npm-optional", "npm-peer", "npm-bundled", "npm-no-pkg"],
        path: "^(react|react-dom|next)(/|$)",
      },
    },
    {
      name: "application-no-adapters-or-next",
      comment:
        "Application depende de puertos/contratos; no de adaptadores concretos ni de Next.js.",
      severity: "error",
      from: { path: "(^|/|\\\\)src(/|\\\\)application(/|\\\\|$)" },
      to: {
        path: "(^|/|\\\\)src(/|\\\\)(adapters|composition)(/|\\\\|$)|(^|/)next(/|$)|(^)react(/|$)",
      },
    },
    {
      name: "ports-no-adapters",
      comment: "Los puertos son contratos; no importan adaptadores ni composition.",
      severity: "error",
      from: { path: "(^|/|\\\\)src(/|\\\\)ports(/|\\\\|$)" },
      to: {
        path: "(^|/|\\\\)src(/|\\\\)(adapters|composition|infrastructure|presentation)(/|\\\\|$)",
      },
    },
    {
      name: "no-direct-database-from-ui",
      comment:
        "Presentación / App Router no acceden a BD ni SDK de persistencia (Supabase client, prisma, etc.).",
      severity: "error",
      from: {
        path: "(^|/|\\\\)src(/|\\\\)(presentation|app|shared)(/|\\\\|$)",
      },
      to: {
        path: "(@supabase|supabase-js|prisma|drizzle-orm|pg(/|$)|postgres)",
      },
    },
    {
      name: "presentation-prefer-ports-over-adapters",
      comment:
        "UI/App Router no deben acoplarse a adaptadores HTTP concretos; usar composition/ports. " +
        "Severidad error: hallazgo real si existe (no se excluye).",
      severity: "error",
      from: {
        path: "(^|/|\\\\)src(/|\\\\)(presentation|app)(/|\\\\|$)",
        pathNot: "\\.(test|spec)\\.(ts|tsx)$",
      },
      to: {
        path: "(^|/|\\\\)src(/|\\\\)adapters(/|\\\\|$)",
      },
    },
    {
      name: "no-circular",
      comment: "Dependencias circulares entre módulos del frontend.",
      severity: "error",
      from: {},
      to: { circular: true },
    },
  ],
  options: {
    doNotFollow: {
      path: "node_modules",
      dependencyTypes: ["npm", "npm-dev", "npm-optional", "npm-peer", "npm-bundled", "npm-no-pkg"],
    },
    tsConfig: {
      fileName: "tsconfig.json",
    },
    enhancedResolveOptions: {
      exportsFields: ["exports"],
      conditionNames: ["import", "require", "node", "default", "types"],
      mainFields: ["module", "main", "types", "typings"],
    },
    reporterOptions: {
      archi: {
        collapsePattern: "^(node_modules|src/[^/]+)",
      },
    },
  },
};
