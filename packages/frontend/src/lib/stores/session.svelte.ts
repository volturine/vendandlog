import { invalidate } from '$app/navigation';
import { api, getActingAs, setActingAs } from '$lib/api';
import type { UserPublic } from '$lib/types';

function createSessionStore() {
	let users = $state<UserPublic[]>([]);
	let actingAs = $state<string | null>(null);
	let loaded = $state(false);

	let theme = $state<'light' | 'dark'>(
		typeof localStorage !== 'undefined' && localStorage.getItem('vdl-theme') === 'dark'
			? 'dark'
			: 'light'
	);

	return {
		get users() {
			return users;
		},
		get actingAs() {
			return actingAs;
		},
		get me(): UserPublic | null {
			return users.find((u) => u.handle === actingAs) ?? null;
		},
		get loaded() {
			return loaded;
		},
		get theme() {
			return theme;
		},
		async load() {
			if (loaded) return;
			actingAs = getActingAs();
			try {
				users = await api.users();
				if (!actingAs || !users.some((u) => u.handle === actingAs)) {
					actingAs = users[0]?.handle ?? null;
					setActingAs(actingAs);
				}
			} finally {
				loaded = true;
			}
		},
		switchUser(handle: string) {
			actingAs = handle;
			setActingAs(handle);
			// Loads that declared depends('vdl:session') refetch with the new identity.
			void invalidate('vdl:session');
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
