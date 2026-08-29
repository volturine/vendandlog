<script lang="ts">
	import { goto } from '$app/navigation';
	import { api, ApiError } from '$lib/api';
	import { session } from '$lib/stores/session.svelte';
	import { CATEGORY_COLORS, categoryLabel } from '$lib/format';

	let title = $state('');
	let description = $state('');
	let price = $state<string>('');
	let condition = $state<'like_new' | 'good' | 'fair'>('good');
	let category = $state('bikes');
	let location = $state('');
	let imageUrl = $state('');
	let busy = $state(false);
	let error = $state<string | null>(null);

	const categoryEntries = Object.entries(CATEGORY_COLORS);

	async function submit(event: SubmitEvent) {
		event.preventDefault();
		if (!session.me) {
			error = 'Pick an identity in the header first';
			return;
		}
		busy = true;
		error = null;
		try {
			const listing = await api.createListing({
				title,
				description,
				price: parseFloat(price),
				condition,
				category,
				location,
				image_url: imageUrl || undefined
			});
			goto(`/listings/${listing.id}`);
		} catch (e) {
			error = e instanceof ApiError ? e.message : 'Failed to create listing';
		} finally {
			busy = false;
		}
	}
</script>

<svelte:head>
	<title>Post a listing — Vendandlog</title>
</svelte:head>

<main class="mx-auto max-w-xl px-5 pb-20 pt-8">
	<h1 class="font-display text-3xl font-medium tracking-tight">Post a listing</h1>
	<p class="mt-2 text-[0.9rem] leading-relaxed text-[var(--vdl-text-muted)]">
		Once posted, your listing joins the public record — edits are logged, and it stays browsable
		even after it sells.
	</p>

	{#if !session.me}
		<p
			class="mt-6 rounded-xl border border-dashed border-[var(--vdl-border)] bg-[var(--vdl-surface)] p-4 text-[0.85rem]"
		>
			Pick an identity in the header first (demo auth).
		</p>
	{:else}
		<form class="mt-6 space-y-4" onsubmit={submit}>
			<label class="block">
				<span class="mb-1 block text-[0.78rem] font-semibold">Title</span>
				<input
					class="vdl-input w-full"
					bind:value={title}
					required
					minlength={6}
					placeholder="Canyon Endurace AL 7.0 — 54cm"
				/>
			</label>

			<label class="block">
				<span class="mb-1 block text-[0.78rem] font-semibold">Description</span>
				<textarea
					class="vdl-input w-full min-h-32"
					bind:value={description}
					required
					placeholder="Condition, history, why you're selling…"></textarea>
			</label>

			<div class="grid grid-cols-2 gap-3">
				<label class="block">
					<span class="mb-1 block text-[0.78rem] font-semibold">Price (USD)</span>
					<input
						class="vdl-input w-full"
						type="number"
						min="1"
						step="0.01"
						bind:value={price}
						required
						placeholder="340"
					/>
				</label>
				<label class="block">
					<span class="mb-1 block text-[0.78rem] font-semibold">Location</span>
					<input class="vdl-input w-full" bind:value={location} placeholder="Kreuzberg · 2 km" />
				</label>
			</div>

			<div class="grid grid-cols-2 gap-3">
				<label class="block">
					<span class="mb-1 block text-[0.78rem] font-semibold">Condition</span>
					<select class="vdl-input w-full" bind:value={condition}>
						<option value="like_new">Like new</option>
						<option value="good">Good</option>
						<option value="fair">Fair</option>
					</select>
				</label>
				<label class="block">
					<span class="mb-1 block text-[0.78rem] font-semibold">Category</span>
					<select class="vdl-input w-full" bind:value={category}>
						{#each categoryEntries as [key] (key)}
							<option value={key}>{categoryLabel(key)}</option>
						{/each}
					</select>
				</label>
			</div>

			<label class="block">
				<span class="mb-1 block text-[0.78rem] font-semibold"
					>Photo URL <span class="font-normal text-[var(--vdl-text-faint)]">(optional)</span></span
				>
				<input class="vdl-input w-full" bind:value={imageUrl} placeholder="https://…" />
			</label>

			{#if error}
				<p
					class="rounded-lg bg-[var(--vdl-danger-subtle)] p-3 text-[0.85rem] text-[var(--vdl-danger)]"
				>
					{error}
				</p>
			{/if}

			<button
				class="vdl-button vdl-button-primary w-full"
				disabled={busy || !title || !description || !price}
			>
				{busy ? 'Posting…' : 'Post to the bazaar'}
			</button>
		</form>
	{/if}
</main>
