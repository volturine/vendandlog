<script lang="ts">
	import { goto } from '$app/navigation';
	import { session } from '$lib/stores/session.svelte';

	let query = $state('');

	function submitSearch(event: SubmitEvent) {
		event.preventDefault();
		const params = new URLSearchParams();
		if (query.trim()) params.set('q', query.trim());
		const qs = params.toString();
		goto(qs ? `/?${qs}` : '/');
	}
</script>

<header class="sticky top-0 z-50 border-b border-[var(--vdl-border-soft)] bg-[var(--vdl-bg)]">
	<div class="mx-auto flex h-16 max-w-7xl items-center gap-3 px-5">
		<a href="/" class="flex shrink-0 items-center gap-2.5 text-[1.1rem] font-bold tracking-tight">
			<span
				class="grid h-8 w-8 place-items-center rounded-[0.55rem] bg-gradient-to-br from-[var(--keep-teal)] to-[var(--keep-blue)] text-[0.95rem] font-bold text-[#173a4a]"
			>
				vdl
			</span>
			<span class="hidden sm:block">vendand<span class="text-[var(--vdl-accent)]">log</span></span>
		</a>

		<form class="flex max-w-md flex-1 items-center" onsubmit={submitSearch} role="search">
			<label
				class="flex w-full items-center gap-2 rounded-full border border-transparent bg-[var(--vdl-surface)] px-4 py-2 transition-colors hover:bg-[var(--vdl-surface-2)] focus-within:border-[var(--vdl-accent)] focus-within:bg-[var(--vdl-bg)]"
			>
				<svg
					class="h-4 w-4 shrink-0 text-[var(--vdl-text-muted)]"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
				>
					<circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" />
				</svg>
				<input
					class="w-full min-w-0 border-none bg-transparent text-[0.9rem] text-[var(--vdl-text)] outline-none placeholder:text-[var(--vdl-text-faint)]"
					placeholder="Search the bazaar — every listing, ever"
					bind:value={query}
				/>
			</label>
		</form>

		<div class="ml-auto flex items-center gap-1">
			<a href="/listings/new" class="vdl-button vdl-button-primary hidden md:inline-flex">
				<svg
					class="h-4 w-4"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
				>
					<path d="M12 5v14M5 12h14" />
				</svg>
				Post listing
			</a>
			<button
				class="grid h-9 w-9 place-items-center rounded-full text-[var(--vdl-text-muted)] transition-colors hover:bg-[var(--vdl-hover)] hover:text-[var(--vdl-text)]"
				onclick={() => session.toggleTheme()}
				aria-label="Toggle theme"
				title="Toggle theme"
			>
				{#if session.theme === 'dark'}
					<svg
						class="h-5 w-5"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
					>
						<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
					</svg>
				{:else}
					<svg
						class="h-5 w-5"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
					>
						<circle cx="12" cy="12" r="4.5" /><path
							d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.6 4.6l1.8 1.8M17.6 17.6l1.8 1.8M19.4 4.6l-1.8 1.8M6.4 17.6l-1.8 1.8"
						/>
					</svg>
				{/if}
			</button>
			{#if session.me}
				<div class="mx-2 hidden h-6 w-px bg-[var(--vdl-border)] sm:block" aria-hidden="true"></div>
				<select
					class="cursor-pointer rounded-full bg-transparent px-2 py-1.5 text-[0.8rem] font-medium text-[var(--vdl-text-muted)] outline-none transition-colors hover:bg-[var(--vdl-hover)] hover:text-[var(--vdl-text)]"
					title="Acting as (demo identity)"
					value={session.actingAs ?? ''}
					onchange={(e) => session.switchUser(e.currentTarget.value)}
				>
					{#each session.users as user (user.handle)}
						<option value={user.handle}>{user.name}</option>
					{/each}
				</select>
			{/if}
		</div>
	</div>
</header>
