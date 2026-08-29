<script lang="ts">
	import type { UserPublic } from '$lib/types';

	let { user, size = 'sm' }: { user: UserPublic; size?: 'sm' | 'md' } = $props();

	const initials = $derived(
		user.name
			.split(' ')
			.map((part) => part[0])
			.slice(0, 2)
			.join('')
			.toUpperCase()
	);
	const dotColor = $derived(user.flags_upheld > 0 ? 'bad' : user.positive_pct < 90 ? 'warn' : 'ok');
</script>

<span class="inline-flex items-center gap-1.5 text-[0.78rem]">
	<span
		class="grid place-items-center rounded-full font-bold text-white/90 {size === 'md'
			? 'h-7 w-7 text-[0.6rem]'
			: 'h-5 w-5 text-[0.5rem]'}"
		style="background:{user.avatar_color}"
	>
		{initials}
	</span>
	<a href="/users/{user.handle}" class="font-semibold hover:underline">{user.handle}</a>
	<span
		class="h-2 w-2 rounded-full {dotColor === 'ok'
			? 'bg-[var(--vdl-success)]'
			: dotColor === 'warn'
				? 'bg-amber-500'
				: 'bg-[var(--vdl-danger)]'}"
	></span>
	<span class="text-[var(--vdl-text-muted)]">{user.trust_score} trust</span>
	{#if user.verified}
		<span class="vdl-pill vdl-pill-blue">verified</span>
	{/if}
</span>
