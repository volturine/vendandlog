<script lang="ts">
	import { goto } from '$app/navigation';
	import { navigating } from '$app/state';
	import type { BrowseParams } from '$lib/types';
	import { CATEGORY_COLORS, categoryLabel, formatPrice, timeAgo } from '$lib/format';
	import ListingCard from '$lib/components/ListingCard.svelte';

	let { data } = $props();

	let view = $state<'grid' | 'list'>('grid');

	// The search input is user-owned state, intentionally initialized from the URL once;
	// afterwards it only changes through the oninput handler (which drives the URL).
	// svelte-ignore state_referenced_locally
	let query = $state(data.q);

	const categoryEntries = Object.entries(CATEGORY_COLORS).filter(([key]) => key !== 'other');

	function buildUrl(next: { q?: string; category?: string; status?: string; sort?: string }): string {
		const merged = {
			q: next.q ?? query.trim(),
			category: next.category ?? data.category,
			status: next.status ?? data.status,
			sort: next.sort ?? data.sort
		};
		const params = new URLSearchParams();
		if (merged.q) params.set('q', merged.q);
		if (merged.category && merged.category !== 'all') params.set('category', merged.category);
		if (merged.status && merged.status !== 'active') params.set('status', merged.status);
		if (merged.sort && merged.sort !== 'recent') params.set('sort', merged.sort);
		const qs = params.toString();
		return qs ? `/?${qs}` : '/';
	}

	let debounce: ReturnType<typeof setTimeout> | undefined;
	function onSearchInput(event: Event & { currentTarget: HTMLInputElement }) {
		query = event.currentTarget.value;
		clearTimeout(debounce);
		debounce = setTimeout(() => {
			goto(buildUrl({ q: query }), { keepFocus: true, noScroll: true });
		}, 250);
	}

	function pickCategory(key: string) {
		goto(buildUrl({ category: key }), { noScroll: true });
	}

	function pickSort(value: string) {
		goto(buildUrl({ sort: value }), { noScroll: true });
	}

	const loading = $derived(navigating.to?.route?.id === '/');
</script>

<svelte:head>
	<title>Vendandlog — the bazaar that remembers</title>
</svelte:head>

<div class="mx-auto max-w-7xl px-5 pb-16 pt-6">
	<!-- Atelier-style editorial hero, compact -->
	<section class="mb-8 text-center">
		<h1 class="font-display mx-auto max-w-xl text-3xl font-medium tracking-tight sm:text-4xl">
			Everything sold. <em class="text-[var(--vdl-accent)]">Nothing forgotten.</em>
		</h1>
		<p class="mx-auto mt-2 max-w-lg text-[0.9rem] leading-relaxed text-[var(--vdl-text-muted)]">
			Every listing, negotiation and outcome stays public — trust here is a record you can inspect.
		</p>
	</section>

	<!-- category chips -->
	<div class="mb-5 flex gap-2 overflow-x-auto pb-1 [scrollbar-width:none]">
		<button class="chip" class:on={data.category === 'all'} onclick={() => pickCategory('all')}>All</button>
		{#each categoryEntries as [key, color] (key)}
			<button class="chip" class:on={data.category === key} onclick={() => pickCategory(key)}>
				<span class="h-2 w-2 rounded-full" style="background:{color}"></span>
				{categoryLabel(key)}
			</button>
		{/each}
	</div>

	<div class="mb-4 flex flex-wrap items-center gap-3">
		<h2 class="text-xl font-bold tracking-tight">
			{data.category === 'all' ? 'Browse' : categoryLabel(data.category)}
		</h2>
		<span class="text-[0.8rem] text-[var(--vdl-text-faint)]">
			{loading ? '…' : `${data.listings.length} listings`}
		</span>

		<div class="ml-auto flex items-center gap-2">
			<select
				class="vdl-input !w-auto !py-1.5 text-[0.82rem]"
				value={data.sort}
				onchange={(e) => pickSort(e.currentTarget.value)}
			>
				<option value="recent">Recently updated</option>
				<option value="price_asc">Price: low → high</option>
				<option value="price_desc">Price: high → low</option>
				<option value="events">Most events in log</option>
			</select>
			<div class="flex rounded-full bg-[var(--vdl-surface)] p-0.5">
				<button
					class="grid h-8 w-9 place-items-center rounded-full {view === 'grid'
						? 'bg-[var(--vdl-bg)] text-[var(--vdl-text)] shadow-sm'
						: 'text-[var(--vdl-text-faint)]'}"
					onclick={() => (view = 'grid')}
					aria-label="Grid view"
				>
					<svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<rect x="3" y="3" width="7.5" height="7.5" rx="1.5" /><rect x="13.5" y="3" width="7.5" height="7.5" rx="1.5" />
						<rect x="3" y="13.5" width="7.5" height="7.5" rx="1.5" /><rect x="13.5" y="13.5" width="7.5" height="7.5" rx="1.5" />
					</svg>
				</button>
				<button
					class="grid h-8 w-9 place-items-center rounded-full {view === 'list'
						? 'bg-[var(--vdl-bg)] text-[var(--vdl-text)] shadow-sm'
						: 'text-[var(--vdl-text-faint)]'}"
					onclick={() => (view = 'list')}
					aria-label="List view"
				>
					<svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
						<path d="M4 6h16M4 12h16M4 18h16" />
					</svg>
				</button>
			</div>
		</div>
	</div>

	{#if view === 'grid'}
		<div class="grid grid-cols-[repeat(auto-fill,minmax(248px,1fr))] gap-4">
			{#each data.listings as listing (listing.id)}
				<ListingCard {listing} />
			{/each}
		</div>
	{:else}
		<div class="vdl-card divide-y divide-[var(--vdl-border-soft)] overflow-hidden !rounded-xl">
			{#each data.listings as listing, i (listing.id)}
				<a href="/listings/{listing.id}" class="flex items-start gap-3 px-4 py-3 transition-colors hover:bg-[var(--vdl-surface)]">
					<span class="w-6 shrink-0 pt-0.5 text-right text-[0.82rem] text-[var(--vdl-text-faint)]">{i + 1}.</span>
					{#if listing.image_url}
						<img src={listing.image_url} alt="" class="h-[52px] w-[70px] shrink-0 rounded object-cover" loading="lazy" />
					{/if}
					<div class="min-w-0 flex-1">
						<p class="text-[0.92rem] font-medium leading-snug">
							{listing.title}
							<span class="ml-1 font-bold">{formatPrice(listing.price_cents)}</span>
							{#if listing.status === 'sold'}
								<span class="vdl-pill vdl-pill-green ml-1">SOLD</span>
							{/if}
						</p>
						<p class="mt-1 flex flex-wrap items-center gap-x-2 gap-y-0.5 text-[0.74rem] text-[var(--vdl-text-faint)]">
							<span class="font-semibold text-[var(--vdl-text-muted)]">{listing.seller.handle} · {listing.seller.trust_score}</span>
							<span>{listing.location}</span>
							<span>{listing.event_count} events in log</span>
							{#if listing.public_conversation_count > 0}
								<span class="text-[var(--vdl-accent)]">{listing.public_conversation_count} conversations public</span>
							{/if}
						</p>
					</div>
					<div class="flex shrink-0 flex-col items-end text-[0.72rem] text-[var(--vdl-text-faint)]">
						<span class="flex items-center gap-1 font-semibold text-[var(--vdl-text-muted)]">
							<svg class="h-3 w-3 text-[var(--vdl-accent)]" viewBox="0 0 24 24" fill="currentColor"><path d="M12 4l8 14H4z" /></svg>
							{listing.event_count * 7 + 5}
						</span>
						<span>{listing.last_event ? timeAgo(listing.last_event.created_at) : timeAgo(listing.updated_at)}</span>
					</div>
				</a>
			{/each}
		</div>
	{/if}

	<div class="mt-8 flex items-center gap-2 rounded-xl border border-dashed border-[var(--vdl-border)] bg-[var(--vdl-surface)] px-4 py-3 text-[0.8rem] text-[var(--vdl-text-muted)]">
		<svg class="h-4 w-4 shrink-0 text-[var(--vdl-accent)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
			<path d="M12 3l8 4v5c0 5-3.5 8-8 9-4.5-1-8-4-8-9V7z" /><path d="M9 12l2 2 4-4" />
		</svg>
		Nothing here can be quietly deleted. Sold listings, negotiations and ratings stay public.
	</div>
</div>

<style>
	.chip {
		display: inline-flex;
		align-items: center;
		gap: 0.45rem;
		white-space: nowrap;
		border: 1px solid var(--vdl-border-soft);
		border-radius: 9999px;
		padding: 0.42rem 0.9rem;
		font-size: 0.82rem;
		font-weight: 500;
		color: var(--vdl-text-muted);
		background: var(--vdl-bg);
		transition:
			background 120ms,
			color 120ms,
			border-color 120ms;
	}
	.chip:hover {
		background: var(--vdl-hover);
		color: var(--vdl-text);
	}
	.chip.on {
		background: var(--vdl-text);
		color: var(--vdl-bg);
		border-color: var(--vdl-text);
		font-weight: 600;
	}
</style>
