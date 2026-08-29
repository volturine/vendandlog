<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import { api } from '$lib/api';
	import { session } from '$lib/stores/session.svelte';
	import { CONDITION_LABEL, categoryColor, categoryLabel, formatPrice, timeAgo } from '$lib/format';
	import TrustChip from '$lib/components/TrustChip.svelte';

	let { data } = $props();

	let tab = $state<'description' | 'conversation' | 'history'>('description');
	let messageDraft = $state<Record<number, string>>({});
	let busy = $state(false);
	let notice = $state<string | null>(null);
	let ratingStars = $state(5);
	let ratingText = $state('');

	const listing = $derived(data.listing);
	const conversationDetails = $derived(data.conversationDetails);
	const isSeller = $derived(!!session.me && listing.seller.handle === session.me.handle);
	const isParticipant = $derived(
		!!session.me && (!!isSeller || listing.conversations.some((c) => c.buyer_handle === session.me?.handle))
	);
	const dropPct = $derived(
		listing.previous_price_cents && listing.previous_price_cents > listing.price_cents
			? Math.round((100 * (listing.previous_price_cents - listing.price_cents)) / listing.previous_price_cents)
			: null
	);
	const eventTone: Record<string, string> = {
		sold: 'green',
		verified: 'green',
		conversation_public: 'warn',
		withdrawn: 'red'
	};

	async function startConversation() {
		await api.startConversation(listing.id, '');
		await invalidateAll();
		tab = 'conversation';
	}

	async function sendMessage(conversationId: number) {
		const body = messageDraft[conversationId]?.trim();
		if (!body) return;
		busy = true;
		try {
			await api.sendMessage(conversationId, body);
			messageDraft[conversationId] = '';
			await invalidateAll();
		} finally {
			busy = false;
		}
	}

	async function unhide(conversationId: number) {
		await api.unhideConversation(conversationId);
		await invalidateAll();
		notice = 'Conversation is now public — it is logged on the listing record.';
	}

	async function markSold() {
		busy = true;
		try {
			await api.changeStatus(listing.id, 'sold');
			await invalidateAll();
			notice = 'Sold. All conversations on this listing are now public.';
		} finally {
			busy = false;
		}
	}

	async function withdraw() {
		busy = true;
		try {
			await api.changeStatus(listing.id, 'withdrawn');
			await invalidateAll();
		} finally {
			busy = false;
		}
	}

	async function submitRating(event: SubmitEvent) {
		event.preventDefault();
		busy = true;
		try {
			await api.rate(listing.id, ratingStars, ratingText.trim());
			await invalidateAll();
			notice = 'Rating recorded — trust is public, and so is this.';
		} finally {
			busy = false;
		}
	}
</script>

<svelte:head>
	<title>{listing.title} — Vendandlog</title>
</svelte:head>

<main class="mx-auto max-w-6xl px-5 pb-20">
	<nav class="mb-5 flex items-center gap-2 text-[0.78rem] text-[var(--vdl-text-faint)]" aria-label="Breadcrumb">
		<a href="/" class="hover:text-[var(--vdl-accent)]">Browse</a>
		<span>›</span>
		<span>{categoryLabel(listing.category)}</span>
		<span>›</span>
		<span class="text-[var(--vdl-text-muted)]">#{listing.id}</span>
	</nav>

	<div class="grid gap-7 lg:grid-cols-[7fr_5fr]">
		<section>
			<div class="vdl-card overflow-hidden !rounded-2xl">
				{#if listing.image_url}
					<img src={listing.image_url} alt={listing.title} class="aspect-[4/3] w-full object-cover" />
				{:else}
					<div class="grid aspect-[4/3] w-full place-items-center bg-[var(--vdl-surface-2)] text-[var(--vdl-text-faint)]">
						no photo
					</div>
				{/if}
			</div>

			<div class="mt-6 flex gap-1 border-b border-[var(--vdl-border-soft)]">
				<button class="tab" class:on={tab === 'description'} onclick={() => (tab = 'description')}>Description</button>
				<button class="tab" class:on={tab === 'conversation'} onclick={() => (tab = 'conversation')}>
					Conversations <span class="count">{listing.conversations.length}</span>
				</button>
				<button class="tab" class:on={tab === 'history'} onclick={() => (tab = 'history')}>
					History <span class="count">{listing.events.length}</span>
				</button>
			</div>

			{#if tab === 'description'}
				<div class="vdl-card p-5 !rounded-none !rounded-b-xl !border-t-0 !shadow-none">
					<p class="whitespace-pre-line text-[0.92rem] leading-relaxed">{listing.description}</p>
					<dl class="mt-5 grid grid-cols-[auto_1fr] gap-x-6 gap-y-1.5 text-[0.84rem]">
						<dt class="text-[var(--vdl-text-faint)]">Condition</dt>
						<dd class="font-medium">{CONDITION_LABEL[listing.condition]}</dd>
						<dt class="text-[var(--vdl-text-faint)]">Location</dt>
						<dd class="font-medium">{listing.location}</dd>
						<dt class="text-[var(--vdl-text-faint)]">Category</dt>
						<dd class="font-medium">
							<span class="inline-block h-2 w-2 rounded-full" style="background:{categoryColor(listing.category)}"></span>
							{categoryLabel(listing.category)}
						</dd>
						<dt class="text-[var(--vdl-text-faint)]">Log</dt>
						<dd class="font-medium">{listing.events.length} events · immutable</dd>
					</dl>
				</div>
			{:else if tab === 'conversation'}
				<div class="space-y-5">
					{#if listing.conversations.length === 0}
						<p class="rounded-xl border border-dashed border-[var(--vdl-border)] bg-[var(--vdl-surface)] p-4 text-[0.85rem] text-[var(--vdl-text-muted)]">
							No conversations yet.
						</p>
					{/if}
					{#each listing.conversations as conversation (conversation.id)}
						{@const detail = conversationDetails[conversation.id]}
						<div class="vdl-card p-4">
							<div class="flex flex-wrap items-center gap-2 border-b border-[var(--vdl-border-soft)] pb-3">
								<strong class="text-[0.9rem]">{conversation.buyer_name}</strong>
								<span class="text-[0.75rem] text-[var(--vdl-text-faint)]">wants to buy · started {timeAgo(conversation.created_at)}</span>
								{#if conversation.is_public}
									<span class="vdl-pill vdl-pill-green">public record</span>
								{:else}
									<span class="vdl-pill vdl-pill-warn">private — goes public on sale</span>
								{/if}
								{#if !conversation.is_public && (isSeller || session.me?.handle === conversation.buyer_handle)}
									<button class="vdl-button vdl-button-quiet ml-auto !px-2 !py-1 text-[0.75rem]" onclick={() => unhide(conversation.id)}>
										Make public now
									</button>
								{/if}
							</div>
							<div class="divide-y divide-[var(--vdl-border-soft)]">
								{#if detail}
									{#each detail.messages as message (message.id)}
										<div class="py-2.5 text-[0.88rem] leading-relaxed">
											<b>{message.author_name}</b>
											<span class="text-[0.72rem] text-[var(--vdl-text-faint)]">· {timeAgo(message.created_at)}</span>
											<p class="mt-0.5">{message.body}</p>
										</div>
									{/each}
								{:else}
									<p class="py-2.5 text-[0.8rem] text-[var(--vdl-text-faint)]">loading messages…</p>
								{/if}
							</div>
							{#if !conversation.is_public && listing.status !== 'sold' && (isSeller || session.me?.handle === conversation.buyer_handle)}
								<form
									class="mt-2 flex gap-2"
									onsubmit={(e) => {
										e.preventDefault();
										sendMessage(conversation.id);
									}}
								>
									<input class="vdl-input flex-1" placeholder="Write a message…" bind:value={messageDraft[conversation.id]} />
									<button class="vdl-button vdl-button-primary" disabled={busy}>Send</button>
								</form>
							{:else if conversation.is_public && listing.status === 'sold'}
								<p class="mt-2 text-[0.75rem] text-[var(--vdl-text-faint)]">This conversation is part of the permanent public record.</p>
							{/if}
						</div>
					{/each}

					{#if session.me && !isSeller && listing.status === 'active' && !listing.conversations.some((c) => c.buyer_handle === session.me?.handle)}
						<button class="vdl-button vdl-button-secondary w-full" onclick={startConversation}>Message the seller</button>
					{/if}
				</div>
			{:else}
				<div class="vdl-card p-5 !rounded-none !rounded-b-xl !border-t-0 !shadow-none">
					<div class="log">
						{#each listing.events as event (event.id)}
							<div class="log-item {eventTone[event.kind] ?? ''}">
								<p class="font-medium leading-snug">{event.summary}</p>
								{#if event.detail}
									<p class="mt-0.5 text-[0.78rem] text-[var(--vdl-text-muted)]">{event.detail}</p>
								{/if}
								<p class="mt-1 flex items-center gap-2 text-[0.72rem] text-[var(--vdl-text-faint)]">
									<span>{timeAgo(event.created_at)}</span>
									<span class="rounded bg-[var(--vdl-surface)] px-1.5 py-0.5 font-mono text-[0.68rem]">#{event.hash}</span>
								</p>
							</div>
						{/each}
					</div>
				</div>
			{/if}
		</section>

		<aside class="space-y-4">
			<div class="vdl-card p-5">
				<div class="flex items-baseline gap-2">
					<span class="text-[1.7rem] font-bold tracking-tight">{formatPrice(listing.price_cents)}</span>
					{#if listing.previous_price_cents && listing.previous_price_cents > listing.price_cents}
						<span class="text-[0.95rem] text-[var(--vdl-text-faint)] line-through">{formatPrice(listing.previous_price_cents)}</span>
					{/if}
				</div>
				{#if dropPct}
					<span class="vdl-pill vdl-pill-green mt-2">↓ dropped {dropPct}%</span>
				{/if}
				<p class="mt-3 text-[1.05rem] font-semibold leading-snug">{listing.title}</p>

				{#if isSeller && listing.status === 'active'}
					<div class="mt-4 flex gap-2">
						<button class="vdl-button vdl-button-primary flex-1" disabled={busy} onclick={markSold}>Mark as sold</button>
						<button class="vdl-button vdl-button-secondary" disabled={busy} onclick={withdraw}>Withdraw</button>
					</div>
				{:else if listing.status === 'sold'}
					<p class="mt-4 rounded-lg bg-[var(--vdl-success-subtle)] p-3 text-[0.8rem] font-medium text-[var(--vdl-success)]">
						Sold {listing.sold_at ? timeAgo(listing.sold_at) : ''} — conversations below are public forever.
					</p>
					{#if session.me && isParticipant && !listing.my_rating}
						<form class="mt-4 space-y-2.5 rounded-xl border border-[var(--vdl-border-soft)] bg-[var(--vdl-surface)] p-3.5" onsubmit={submitRating}>
							<p class="text-[0.82rem] font-semibold">
								Rate {isSeller ? (listing.conversations[0]?.buyer_name ?? 'your buyer') : listing.seller.name}
							</p>
							<div class="flex gap-1">
								{#each [1, 2, 3, 4, 5] as star (star)}
									<button
										type="button"
										class="text-xl {star <= ratingStars ? 'text-amber-500' : 'text-[var(--vdl-border)]'}"
										onclick={() => (ratingStars = star)}
										aria-label="{star} stars"
									>
										★
									</button>
								{/each}
							</div>
							<textarea class="vdl-input w-full min-h-16" bind:value={ratingText} placeholder="How did it go? This becomes public."></textarea>
							<button class="vdl-button vdl-button-primary w-full" disabled={busy}>Submit rating</button>
						</form>
					{:else if listing.my_rating}
						<p class="mt-3 text-[0.78rem] text-[var(--vdl-text-muted)]">
							You rated this counterparty {listing.my_rating.stars}★ — <a class="text-[var(--vdl-accent)] underline" href="/users/{listing.my_rating.ratee_handle}">see their profile</a>.
						</p>
					{/if}
				{:else if listing.status === 'withdrawn'}
					<p class="mt-4 rounded-lg bg-[var(--vdl-warning-subtle)] p-3 text-[0.8rem] font-medium text-[var(--vdl-warning)]">
						Withdrawn — this stays public per the record.
					</p>
				{:else if session.me && !isSeller}
					<button class="vdl-button vdl-button-primary mt-4 w-full" disabled={busy} onclick={startConversation}>
						Message the seller
					</button>
				{/if}

				<div class="mt-4 rounded-xl border border-[var(--vdl-border-soft)] bg-[var(--vdl-surface)] p-3.5">
					<TrustChip user={listing.seller} size="md" />
					<p class="mt-1.5 text-[0.75rem] text-[var(--vdl-text-faint)]">
						{listing.seller.positive_pct}% positive · {listing.seller.sales_count} sales
					</p>
					<a href="/users/{listing.seller.handle}" class="mt-2 inline-block text-[0.8rem] font-medium text-[var(--vdl-accent)] hover:underline">
						View profile →
					</a>
				</div>
			</div>

			{#if listing.similar.length}
				<div class="vdl-card p-4">
					<h3 class="mb-3 text-[0.68rem] font-bold uppercase tracking-[0.09em] text-[var(--vdl-text-faint)]">Similar listings</h3>
					{#each listing.similar as similar (similar.id)}
						<a href="/listings/{similar.id}" class="flex items-center gap-3 rounded-lg p-1.5 transition-colors hover:bg-[var(--vdl-hover)]">
							{#if similar.image_url}
								<img src={similar.image_url} alt="" class="h-12 w-16 rounded object-cover" loading="lazy" />
							{/if}
							<div class="min-w-0">
								<p class="truncate text-[0.82rem] font-medium">{similar.title}</p>
								<p class="text-[0.78rem] font-bold">{formatPrice(similar.price_cents)}</p>
							</div>
						</a>
					{/each}
				</div>
			{/if}
		</aside>
	</div>

	{#if notice}
		<div class="fixed bottom-5 left-1/2 z-50 -translate-x-1/2 rounded-full bg-[var(--vdl-text)] px-5 py-2.5 text-[0.85rem] text-[var(--vdl-bg)] shadow-lg">
			{notice}
			<button class="ml-3 font-bold opacity-70 hover:opacity-100" onclick={() => (notice = null)}>✕</button>
		</div>
	{/if}
</main>

<style>
	.tab {
		padding: 0.55rem 0.9rem;
		font-size: 0.86rem;
		font-weight: 500;
		color: var(--vdl-text-muted);
		border-bottom: 2px solid transparent;
		margin-bottom: -1px;
		transition:
			color 120ms,
			border-color 120ms;
	}
	.tab:hover {
		color: var(--vdl-text);
	}
	.tab.on {
		color: var(--vdl-accent);
		border-color: var(--vdl-accent);
		font-weight: 600;
	}
	.count {
		font-size: 0.68rem;
		background: var(--vdl-surface-2);
		border-radius: 9999px;
		padding: 0.1rem 0.45rem;
		margin-left: 0.3rem;
		color: var(--vdl-text-muted);
	}
	.log {
		position: relative;
		padding-left: 1.35rem;
	}
	.log::before {
		content: '';
		position: absolute;
		left: 0.44rem;
		top: 0.4rem;
		bottom: 0.4rem;
		width: 2px;
		background: var(--vdl-border-soft);
		border-radius: 2px;
	}
	.log-item {
		position: relative;
		padding: 0.45rem 0 0.45rem 0.35rem;
		font-size: 0.84rem;
	}
	.log-item::before {
		content: '';
		position: absolute;
		left: -1.22rem;
		top: 0.78rem;
		width: 0.62rem;
		height: 0.62rem;
		border-radius: 9999px;
		background: var(--vdl-bg);
		border: 2px solid var(--vdl-accent);
	}
	.log-item.green::before {
		border-color: var(--vdl-success);
	}
	.log-item.warn::before {
		border-color: #f59e0b;
	}
	.log-item.red::before {
		border-color: var(--vdl-danger);
	}
</style>
