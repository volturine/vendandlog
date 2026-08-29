<script lang="ts">
	import type { Listing } from '$lib/types';
	import { CONDITION_LABEL, categoryColor, formatPrice, timeAgo } from '$lib/format';
	import TrustChip from '$lib/components/TrustChip.svelte';

	let { listing }: { listing: Listing } = $props();

	const dropPct = $derived(
		listing.previous_price_cents && listing.previous_price_cents > listing.price_cents
			? Math.round(
					(100 * (listing.previous_price_cents - listing.price_cents)) /
						listing.previous_price_cents
				)
			: null
	);
</script>

<a
	href="/listings/{listing.id}"
	class="vdl-card vdl-card-hover group flex flex-col overflow-hidden"
>
	<div class="relative aspect-[4/3] bg-[var(--vdl-surface-2)]">
		{#if listing.image_url}
			<img
				src={listing.image_url}
				alt={listing.title}
				loading="lazy"
				class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-[1.03]"
			/>
		{/if}
		{#if listing.status === 'sold'}
			<span
				class="absolute left-2.5 top-2.5 rounded-full bg-[#202124] px-2.5 py-1 text-[0.68rem] font-semibold text-white dark:bg-[#e8eaed] dark:text-[#1a1a1a]"
			>
				Sold {listing.sold_at ? `· ${timeAgo(listing.sold_at)}` : ''}
			</span>
		{:else}
			<span
				class="absolute left-2.5 top-2.5 rounded-full bg-white/90 px-2.5 py-1 text-[0.68rem] font-semibold text-[#3c4043] backdrop-blur dark:bg-[#202124]/85 dark:text-[#e8eaed]"
			>
				{CONDITION_LABEL[listing.condition]}
			</span>
		{/if}
		<span
			class="absolute bottom-2.5 right-2.5 flex items-center gap-1 rounded-full bg-white/90 px-2 py-1 text-[0.66rem] font-semibold text-[var(--vdl-text-muted)] backdrop-blur dark:bg-[#202124]/85 dark:text-[#9aa0a6]"
		>
			<span class="h-2 w-2 rounded-full" style="background:{categoryColor(listing.category)}"
			></span>
			{listing.category}
		</span>
	</div>

	<div class="flex flex-1 flex-col gap-1.5 px-3.5 pb-2.5 pt-3">
		<div class="flex items-baseline gap-2">
			<span class="text-[1.06rem] font-bold tracking-tight">{formatPrice(listing.price_cents)}</span
			>
			{#if listing.previous_price_cents && listing.previous_price_cents > listing.price_cents}
				<span class="text-[0.78rem] text-[var(--vdl-text-faint)] line-through">
					{formatPrice(listing.previous_price_cents)}
				</span>
				{#if dropPct}
					<span class="vdl-pill vdl-pill-green">↓ {dropPct}%</span>
				{/if}
			{/if}
		</div>
		<h3 class="line-clamp-2 min-h-10 text-[0.9rem] font-medium leading-snug">{listing.title}</h3>
		<p class="mt-auto text-[0.75rem] text-[var(--vdl-text-faint)]">{listing.location}</p>
	</div>

	<div class="border-t border-[var(--vdl-border-soft)] px-3.5 py-2">
		<TrustChip user={listing.seller} />
	</div>

	{#if listing.last_event}
		<div
			class="flex items-center gap-1.5 border-t border-dashed border-[var(--vdl-border-soft)] px-3.5 pb-2.5 pt-2 text-[0.72rem] text-[var(--vdl-text-faint)]"
		>
			<svg
				class="h-3 w-3 shrink-0"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				stroke-linecap="round"
			>
				<path d="M3 12a9 9 0 1 0 3-6.7" /><path d="M3 4v4h4" />
			</svg>
			<span class="truncate text-[var(--vdl-text-muted)]">{listing.last_event.summary}</span>
			<span class="ml-auto shrink-0">{timeAgo(listing.last_event.created_at)}</span>
		</div>
	{/if}
</a>
