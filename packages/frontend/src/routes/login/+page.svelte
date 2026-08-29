<script lang="ts">
	import { goto } from '$app/navigation';
	import { ApiError, api } from '$lib/api';
	import { session } from '$lib/stores/session.svelte';

	let mode = $state<'login' | 'register'>('login');
	let handle = $state('');
	let name = $state('');
	let password = $state('');
	let busy = $state(false);
	let error = $state<string | null>(null);

	async function submit(event: SubmitEvent) {
		event.preventDefault();
		busy = true;
		error = null;
		try {
			if (mode === 'login') {
				await session.login(handle.trim(), password);
			} else {
				await session.register(handle.trim().toLowerCase(), name.trim(), password);
			}
			goto('/');
		} catch (e) {
			error = e instanceof ApiError ? e.message : 'Something went wrong';
		} finally {
			busy = false;
		}
	}
</script>

<svelte:head>
	<title>{mode === 'login' ? 'Sign in' : 'Create account'} — Vendandlog</title>
</svelte:head>

<main class="mx-auto max-w-sm px-4 pb-20 pt-10 sm:px-5 sm:pt-12">
	<h1 class="font-display text-3xl font-medium tracking-tight">
		{mode === 'login' ? 'Welcome back' : 'Join the bazaar'}
	</h1>
	<p class="mt-2 text-[0.88rem] leading-relaxed text-[var(--vdl-text-muted)]">
		{mode === 'login'
			? 'Your handle is your reputation — everything you do here stays on the public record.'
			: 'Pick a handle you will be proud of in ten years. It cannot be changed.'}
	</p>

	{#if session.me}
		<div class="mt-6 rounded-xl border border-[var(--vdl-border-soft)] bg-[var(--vdl-surface)] p-4 text-[0.88rem]">
			You are signed in as <b>@{session.me.handle}</b>.
			<button class="text-[var(--vdl-accent)] underline" onclick={() => session.logout()}>Sign out</button>
			first to switch accounts.
		</div>
	{:else}
		<form class="mt-6 space-y-4" onsubmit={submit}>
			{#if mode === 'register'}
				<label class="block">
					<span class="mb-1 block text-[0.78rem] font-semibold">Name</span>
					<input class="vdl-input w-full" bind:value={name} required placeholder="Jana Bergmann" />
				</label>
			{/if}
			<label class="block">
				<span class="mb-1 block text-[0.78rem] font-semibold">Handle</span>
				<input
					class="vdl-input w-full"
					bind:value={handle}
					required
					pattern="[a-zA-Z0-9][a-zA-Z0-9._-]+"
					title="Lowercase letters, digits, dots, dashes, underscores"
					placeholder="jana.b"
				/>
			</label>
			<label class="block">
				<span class="mb-1 block text-[0.78rem] font-semibold">Password</span>
				<input class="vdl-input w-full" type="password" bind:value={password} required minlength={4} />
			</label>

			{#if error}
				<p class="rounded-lg bg-[var(--vdl-danger-subtle)] p-3 text-[0.85rem] text-[var(--vdl-danger)]">{error}</p>
			{/if}

			<button class="vdl-button vdl-button-primary w-full" disabled={busy || !handle || !password}>
				{busy ? '…' : mode === 'login' ? 'Sign in' : 'Create account'}
			</button>
		</form>

		<p class="mt-4 text-center text-[0.85rem] text-[var(--vdl-text-muted)]">
			{#if mode === 'login'}
				New here?
				<button class="font-semibold text-[var(--vdl-accent)] hover:underline" onclick={() => ((mode = 'register'), (error = null))}>
					Create an account
				</button>
			{:else}
				Already have an account?
				<button class="font-semibold text-[var(--vdl-accent)] hover:underline" onclick={() => ((mode = 'login'), (error = null))}>
					Sign in
				</button>
			{/if}
		</p>

		{#if mode === 'login'}
			<p class="mt-6 rounded-xl border border-dashed border-[var(--vdl-border)] bg-[var(--vdl-surface)] p-3.5 text-center text-[0.78rem] text-[var(--vdl-text-faint)]">
				Demo data: try <b class="text-[var(--vdl-text-muted)]">jana.b</b>, <b class="text-[var(--vdl-text-muted)]">milan</b> or <b class="text-[var(--vdl-text-muted)]">lea_rides</b> — password <b class="text-[var(--vdl-text-muted)]">demo</b>
			</p>
		{/if}
	{/if}
</main>
