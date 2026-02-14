import { defineConfig } from "vite";
import { fileURLToPath, URL } from "node:url";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes("node_modules")) return;
          const normalized = id.replace(/\\/g, "/");
          if (normalized.includes("/node_modules/md-editor-v3/")) return "vendor-md-editor-v3";
          if (normalized.includes("/node_modules/@vue-flow/")) return "vendor-vue-flow";
          if (normalized.includes("/node_modules/@unovis/")) return "vendor-unovis";
          if (normalized.includes("/node_modules/reka-ui/")) return "vendor-reka-ui";
          if (normalized.includes("/node_modules/vue-router/")) return "vendor-vue-router";
          if (normalized.includes("/node_modules/pinia/")) return "vendor-pinia";
          if (normalized.includes("/node_modules/axios/")) return "vendor-axios";
          if (normalized.includes("/node_modules/@codemirror/")) return "vendor-codemirror";
          if (normalized.includes("/node_modules/@lezer/")) return "vendor-lezer";
          if (normalized.includes("/node_modules/codemirror/")) return "vendor-codemirror-legacy";
          if (normalized.includes("/node_modules/markdown-it/")) return "vendor-markdown-it";
          if (normalized.includes("/node_modules/vue/")) return "vendor-vue";
        }
      }
    }
  },
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url))
    }
  },
  server: {
    host: "0.0.0.0",
    port: 5173,
    proxy: {
      "/api": {
        target: "http://192.168.5.111:8000",
        changeOrigin: true
      }
    }
  }
});
