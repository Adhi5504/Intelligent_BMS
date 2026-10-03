import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// host: true + allowedHosts: true lets Cloudflare/ngrok tunnel hostnames reach the dev and preview servers.
export default defineConfig({
  plugins: [react()],
  server: { host: "0.0.0.0", port: 5173, allowedHosts: true },
  preview: { host: "0.0.0.0", port: 4173, allowedHosts: true },
});
