// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from "@tailwindcss/vite";

export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",
  devtools: { enabled: true },
  modules: [
    "@nuxt/eslint",
    "@nuxt/image",
    "@nuxt/icon",
    "@nuxt/fonts",
    "@nuxtjs/color-mode",
    "@nuxtjs/i18n",
  ],
  vite: {
    plugins: [tailwindcss()],
  },
  css: ["./app/assets/css/main.css"],
  build: {
    transpile: ["@vue-leaflet/vue-leaflet"],
  },
  i18n: {
    defaultLocale: "en",
    locales: [
      { code: "en", name: "English", file: "en.json" },
      { code: "ro", name: "Romanian", file: "ro.json" },
    ],
    detectBrowserLanguage: {
      useCookie: true,
      alwaysRedirect: true,
      cookieKey: "i18n_redirected",
      redirectOn: "root",
    },
  },
  // Add here custom components so we can use them without importing
  components: [
    "~/components",
    "~/components/dashboard",
    "~/components/ui/button",
    "~/components/ui/switch",
    "~/components/ui/input",
    "~/components/ui/select",
    "~/components/ui/textarea",
    "~/components/ui/field",
    "~/components/ui/form",
    "~/components/ui/navigationmenu",
    "~/components/ui/mobilenavigationmenu",
    "~/components/ui/colorpicker",
    "~/components/ui/popover",
    "~/components/ui/modal",
    "~/components/ui/tabs",
    "~/components/ui/card",
    "~/components/ui/carousel",
    "~/components/ui/tooltip",
    "~/components/ui/grid",
    "~/components/ui/calendar",
    "~/components/ui/sidebar",
    "~/components/ui/table",
    "~/components/ui/badge",
    "~/components/ui/link",
  ],
});

