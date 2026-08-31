<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import { api } from '$lib/api';
	import { session } from '$lib/stores/session.svelte';
	import { timeAgo } from '$lib/format';
	import type { Rating } from '$lib/types';
	import ListingCard from '$lib/components/ListingCard.svelte';

	let { data } = $props();

	let ratingTab = $state<'received' | 'given'>('received');
	let givenRatings = $state<Rating[] | null>(null);
	let givenLoading = $state(false);
	let flagReason = $state('');
	let flagOpen = $state(false);
	let notice = $state<string | null>(null);

	const user = $derived(data.user);
	const ratings = $derived(ratingTab === 'received' ? data.ratings : (givenRatings ?? []));

	async function pickRatingTab(tab: 'received' | 'given') {
		ratingTab = tab;
		if (tab === 'given' && !givenRatings) {
			givenLoading = true;
			try {
				givenRatings = await api.userRatings(user.handle, 'given');
			} finally {
				givenLoading = false;
			}
		}
	}

	async function submitFlag(event: SubmitEvent) {
		event.preventDefault();
		if (!flagReason.trim()) return;
		await api.flagUser(user.handle, flagReason.trim());
		flagOpen = false;
		flagReason = '';
		await invalidateAll();
		notice = 'Flag recorded — it is visible to everyone and lowers the trust score.';
		setTimeout(() => (notice = null), 5000);
	}

	const soldCount = $derived(data.listings.filter((l) => l.status === 'sold').length);
</script>

<svelte:head>
	<title>{user.name} (@{user.handle}) — Vendandlog</title>
</svelte:head>

<main class="mx-auto max-w-4xl px-4 pb-20 sm:px-5">
	<header class="mb-6 mt-4 flex flex-wrap items-center gap-4">
		<span
			class="grid h-16 w-16 place-items-center rounded-full text-xl font-bold"
			style="background:{user.avatar_color};color:#fff"
		>
			{user.name
				.split(' ')
				.map((p) => p[0])
				.slice(0, 2)
				.join('')}
		</span>
		<div>
			<h1 class="text-2xl font-bold tracking-tight">
				{user.name}
				{#if user.verified}<span class="vdl-pill vdl-pill-blue align-middle">verified</span>{/if}
				{#if user.flags_upheld > 0}<span class="vdl-pill vdl-pill-danger align-middle"
						>{user.flags_upheld} flags upheld</span
					>{/if}
			</h1>
			<p class="mt-1 flex flex-wrap items-center gap-2 text-[0.82rem] text-[var(--vdl-text-muted)]">
				<span>{user.positive_pct}% positive · {user.sales_count} sales</span>
				<span>·</span>
				<span
					>member since {new Date(user.created_at).toLocaleDateString('en-US', {
						month: 'long',
						year: 'numeric'
					})}</span
				>
			</p>
			{#if user.bio}<p class="mt-1 max-w-xl text-[0.85rem] text-[var(--vdl-text-muted)]">
					{user.bio}
				</p>{/if}
		</div>
		{#if session.me && session.me.handle !== user.handle}
			<button
				class="vdl-button vdl-button-secondary ml-auto"
				onclick={() => (flagOpen = !flagOpen)}
			>
				Flag user
			</button>
		{/if}
	</header>

	{#if flagOpen}
		<form
			class="mb-6 space-y-2 rounded-xl border border-[var(--vdl-border)] bg-[var(--vdl-surface)] p-4"
			onsubmit={submitFlag}
		>
			<label class="block text-[0.82rem] font-semibold" for="flag-reason"
				>Why are you flagging @{user.handle}? This becomes public.</label
			>
			<input
				id="flag-reason"
				class="vdl-input w-full"
				bind:value={flagReason}
				placeholder="No-show twice — chat history is public proof"
				required
			/>
			<button class="vdl-button vdl-button-primary" disabled={!flagReason.trim()}
				>Submit flag</button
			>
		</form>
	{/if}

	<section class="mb-7 grid grid-cols-2 gap-2.5 sm:grid-cols-4 sm:gap-3">
		<div class="rounded-xl border border-[var(--vdl-border-soft)] bg-[var(--vdl-surface)] p-4">
			<div
				class="text-2xl font-bold tracking-tight"
				class:text-[var(--vdl-success)]={user.flags_upheld === 0}
			>
				{user.trust_score}
			</div>
			<div class="mt-0.5 text-[0.72rem] text-[var(--vdl-text-faint)]">
				trust score, earned in public
			</div>
		</div>
		<div class="rounded-xl border border-[var(--vdl-border-soft)] bg-[var(--vdl-surface)] p-4">
			<div class="text-2xl font-bold tracking-tight">{user.positive_pct}%</div>
			<div class="mt-0.5 text-[0.72rem] text-[var(--vdl-text-faint)]">positive outcomes</div>
		</div>
		<div class="rounded-xl border border-[var(--vdl-border-soft)] bg-[var(--vdl-surface)] p-4">
			<div class="text-2xl font-bold tracking-tight">{soldCount}</div>
			<div class="mt-0.5 text-[0.72rem] text-[var(--vdl-text-faint)]">sales on the record</div>
		</div>
		<div class="rounded-xl border border-[var(--vdl-border-soft)] bg-[var(--vdl-surface)] p-4">
			<div class="text-2xl font-bold tracking-tight">{data.listings.length}</div>
			<div class="mt-0.5 text-[0.72rem] text-[var(--vdl-text-faint)]">listings ever posted</div>
		</div>
	</section>

	<section class="mb-8">
		<h2
			class="mb-3 text-[0.68rem] font-bold uppercase tracking-[0.09em] text-[var(--vdl-text-faint)]"
		>
			Listings — sold ones stay browsable
		</h2>
		{#if data.listings.length === 0}
			<p
				class="rounded-xl border border-dashed border-[var(--vdl-border)] bg-[var(--vdl-surface)] p-4 text-[0.85rem] text-[var(--vdl-text-muted)]"
			>
				Nothing listed yet.
			</p>
		{:else}
			<div class="grid grid-cols-[repeat(auto-fill,minmax(220px,1fr))] gap-4">
				{#each data.listings as listing (listing.id)}
					<ListingCard {listing} />
				{/each}
			</div>
		{/if}
	</section>

	<section>
		<div class="mb-3 flex gap-1 border-b border-[var(--vdl-border-soft)]">
			<button
				class="rtab"
				class:on={ratingTab === 'received'}
				onclick={() => pickRatingTab('received')}>Ratings received</button
			>
			<button class="rtab" class:on={ratingTab === 'given'} onclick={() => pickRatingTab('given')}
				>Ratings given</button
			>
		</div>
		{#if givenLoading}
			<p
				class="rounded-xl border border-dashed border-[var(--vdl-border)] bg-[var(--vdl-surface)] p-4 text-[0.85rem] text-[var(--vdl-text-muted)]"
			>
				Loading…
			</p>
		{:else if ratings.length === 0}
			<p
				class="rounded-xl border border-dashed border-[var(--vdl-border)] bg-[var(--vdl-surface)] p-4 text-[0.85rem] text-[var(--vdl-text-muted)]"
			>
				Nothing here yet.
			</p>
		{:else}
			<div class="vdl-card divide-y divide-[var(--vdl-border-soft)]">
				{#each ratings as rating (rating.id)}
					<div class="flex flex-wrap items-baseline gap-x-3 gap-y-1 px-4 py-3 text-[0.86rem]">
						<span class="font-semibold"
							>{rating.rater_handle === user.handle
								? rating.ratee_handle
								: rating.rater_handle}</span
						>
						<span class="tracking-wider text-amber-500">
							{'★'.repeat(rating.stars)}{'☆'.repeat(5 - rating.stars)}
						</span>
						<span class="min-w-0 flex-1 text-[var(--vdl-text-muted)]">“{rating.text}”</span>
						<span class="text-[0.72rem] text-[var(--vdl-text-faint)]">
							{timeAgo(rating.created_at)} ·
							<a class="hover:underline" href="/listings/{rating.listing_id}"
								>sale #{rating.listing_id}</a
							>
						</span>
					</div>
				{/each}
			</div>
		{/if}
	</section>

	{#if notice}
		<div
			class="fixed bottom-5 left-1/2 z-50 -translate-x-1/2 rounded-full bg-[var(--vdl-text)] px-5 py-2.5 text-[0.85rem] text-[var(--vdl-bg)] shadow-lg"
		>
			{notice}
		</div>
	{/if}
</main>

<style>
	.rtab {
		padding: 0.55rem 0.9rem;
		font-size: 0.86rem;
		font-weight: 500;
		color: var(--vdl-text-muted);
		border-bottom: 2px solid transparent;
		margin-bottom: -1px;
	}
	.rtab:hover {
		color: var(--vdl-text);
	}
	.rtab.on {
		color: var(--vdl-accent);
		border-color: var(--vdl-accent);
		font-weight: 600;
	}
</style>
