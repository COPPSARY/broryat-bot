import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

export default defineConfig({
  site: "https://broryat.tech",
  output: "static",
  trailingSlash: "always",
  integrations: [
    sitemap({
      i18n: {
        defaultLocale: "kh",
        locales: {
          kh: "km-KH",
          en: "en-US",
        },
      },
    }),
  ],
  server: {
    host: true,
    port: 4321,
  },
  preview: {
    host: true,
    port: 4321,
  },
  vite: {
    server: {
      allowedHosts: [".mekongtunnel.dev"],
    },
    preview: {
      allowedHosts: [".mekongtunnel.dev"],
    },
  },
  i18n: {
    locales: ["kh", "en"],
    defaultLocale: "kh",
    routing: {
      prefixDefaultLocale: false,
    },
  },
});
