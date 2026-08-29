import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

const port = parseInt(process.env.FRONTEND_PORT || '3000', 10);
const apiPort = parseInt(process.env.BACKEND_PORT || '8000', 10);
const apiHost = process.env.BACKEND_HOST || '127.0.0.1';

export default defineConfig({
	plugins: [tailwindcss(), sveltekit()],
	server: {
		host: '0.0.0.0',
		port,
		strictPort: true,
		proxy: {
			'/api': {
				target: `http://${apiHost}:${apiPort}`,
				changeOrigin: true
			}
		}
	},
	preview: {
		host: '0.0.0.0',
		port,
		strictPort: true,
		proxy: {
			'/api': {
				target: `http://${apiHost}:${apiPort}`,
				changeOrigin: true
			}
		}
	}
});
