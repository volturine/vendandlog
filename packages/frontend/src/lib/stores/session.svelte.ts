import { invalidate } from '$app/navigation';
import { api } from '$lib/api';
import type { UserPublic } from '$lib/types';

function createSessionStore() {
	let me = $state<UserPublic | null>(null);
	let loaded = $state(false);

	let theme = $state<'light' | 'dark'>(
		typeof localStorage !== 'undefined' && localStorage.getItem('vdl-theme') === 'dark'
			? 'dark'
			: 'light'
	);

	return {
		get me() {
			return me;
		},
		get loaded() {
			return loaded;
		},
		get theme() {
			return theme;
		},
		async load() {
			try {
				me = await api.me();
			} finally {
				loaded = true;
			}
		},
		async login(handle: string, password: string) {
			me = await api.login({ handle, password });
			await invalidate('vdl:session');
		},
		async register(handle: string, name: string, password: string) {
			me = await api.register({ handle, name, password });
			await invalidate('vdl:session');
		},
		async logout() {
			await api.logout();
			me = null;
			await invalidate('vdl:session');
		},
		toggleTheme() {
			theme = theme === 'dark' ? 'light' : 'dark';
			localStorage.setItem('vdl-theme', theme);
			document.documentElement.classList.toggle('dark', theme === 'dark');
		},
		applyTheme() {
			document.documentElement.classList.toggle('dark', theme === 'dark');
		}
	};
}

export const session = createSessionStore();
