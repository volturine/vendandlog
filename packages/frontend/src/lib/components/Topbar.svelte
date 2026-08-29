<script lang="ts">
	import { goto } from '$app/navigation';
	import { session } from '$lib/stores/session.svelte';

	let query = $state('');
	let menu: HTMLDetailsElement | undefined = $state();

	function submitSearch(event: SubmitEvent) {
		event.preventDefault();
		const params = new URLSearchParams();
		if (query.trim()) params.set('q', query.trim());
		const qs = params.toString();
		goto(qs ? `/?${qs}` : '/');
	}

	async function signOut() {
		menu?.removeAttribute('open');
		await session.logout();
	}
</script>

<header class="sticky top-0 z-50 border-b border-[var(--vdl-border-soft)] bg-[var(--vdl-bg)]">
	<div class="mx-auto flex h-14 max-w-7xl items-center gap-2 px-4 sm:px-5">
		<a href="/" class="flex shrink-0 items-center gap-2.5 text-[1.05rem] font-bold tracking-tight">
			<span
				class="grid h-8 w-8 place-items-center rounded-[0.55rem] bg-gradient-to-br from-[var(--keep-teal)] to-[var(--keep-blue)] text-[0.9rem] font-bold text-[#173a4a]"
			>
				vdl
			</span>
			<span class="hidden md:block">vendand<span class="text-[var(--vdl-accent)]">log</span></span>
		</a>

		<form
			class="flex min-w-0 flex-1 items-center md:mx-auto md:max-w-lg"
			onsubmit={submitSearch}
			role="search"
		>
			<label
				class="flex w-full items-center gap-2 rounded-full border border-transparent bg-[var(--vdl-surface)] px-3.5 py-1.5 transition-colors hover:bg-[var(--vdl-surface-2)] focus-within:border-[var(--vdl-accent)] focus-within:bg-[var(--vdl-bg)] sm:px-4"
			>
				<svg class="h-4 w-4 shrink-0 text-[var(--vdl-text-muted)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
					<circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" />
				</svg>
				<input
					class="w-full min-w-0 border-none bg-transparent text-[0.88rem] text-[var(--vdl-text)] outline-none placeholder:text-[var(--vdl-text-faint)]"
					placeholder="Search the bazaar"
					bind:value={query}
				/>
			</label>
		</form>

		<div class="ml-auto flex shrink-0 items-center gap-0.5 sm:gap-1">
			<a href="/listings/new" class="vdl-button vdl-button-primary hidden md:inline-flex">
				<svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
					<path d="M12 5v14M5 12h14" />
				</svg>
				Post listing
			</a>
			<a
				href="/listings/new"
				class="grid h-9 w-9 place-items-center rounded-full text-[var(--vdl-accent)] transition-colors hover:bg-[var(--vdl-hover)] md:hidden"
				aria-label="Post listing"
			>
				<svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
					<path d="M12 5v14M5 12h14" />
				</svg>
			</a>
			<button
				class="grid h-9 w-9 place-items-center rounded-full text-[var(--vdl-text-muted)] transition-colors hover:bg-[var(--vdl-hover)] hover:text-[var(--vdl-text)]"
				onclick={() => session.toggleTheme()}
				aria-label="Toggle theme"
				title="Toggle theme"
			>
				{#if session.theme === 'dark'}
					<svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
						<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
					</svg>
				{:else}
					<svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
						<circle cx="12" cy="12" r="4.5" /><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.6 4.6l1.8 1.8M17.6 17.6l1.8 1.8M19.4 4.6l-1.8 1.8M6.4 17.6l-1.8 1.8" />
					</svg>
				{/if}
			</button>

			{#if session.loaded}
				{#if session.me}
					<details class="account relative" bind:this={menu}>
						<summary
							class="grid h-9 w-9 cursor-pointer list-none place-items-center rounded-full text-[0.72rem] font-bold text-white/90"
							style="background:{session.me.avatar_color}"
							title="@{session.me.handle}"
						>
							{session.me.name.split(' ').map((p) => p[0]).slice(0, 2).join('')}
						</summary>
						<div class="absolute right-0 top-11 z-50 w-56 overflow-hidden rounded-xl border border-[var(--vdl-border-soft)] bg-[var(--vdl-bg)] shadow-[var(--vdl-elevation-popover)]">
							<div class="border-b border-[var(--vdl-border-soft)] px-4 py-3">
								<p class="truncate text-[0.88rem] font-semibold">{session.me.name}</p>
								<p class="text-[0.75rem] text-[var(--vdl-text-faint)]">@{session.me.handle}</p>
							</div>
							<a
								href="/users/{session.me.handle}"
								class="block px-4 py-2.5 text-[0.86rem] hover:bg-[var(--vdl-hover)]"
								onclick={() => menu?.removeAttribute('open')}
							>
								Your profile
							</a>
							<button
								class="block w-full px-4 py-2.5 text-left text-[0.86rem] text-[var(--vdl-text-muted)] hover:bg-[var(--vdl-hover)]"
								onclick={signOut}
							>
								Sign out
							</button>
						</div>
					</details>
				{:else}
					<a href="/login" class="vdl-button vdl-button-primary !px-3.5">Sign in</a>
				{/if}
			{/if}
		</div>
	</div>
</header>

<style>
	.account summary::-webkit-details-marker {
		display: none;
	}
</style>
