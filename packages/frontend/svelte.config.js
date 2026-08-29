import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	preprocess: vitePreprocess(),

	kit: {
		adapter: adapter({
			pages: 'build',
			assets: 'build',
			fallback: '200.html',
			precompress: false,
			strict: true
		}),
		paths: {
			base: ''
		}
	},

	// Enable runes for all project files; leave dependencies as-is
	vitePlugin: {
		dynamicCompileOptions({ filename }) {
			if (!filename) return;
			if (filename.includes('node_modules')) return;
			return { runes: true };
		}
	}
};

export default config;
