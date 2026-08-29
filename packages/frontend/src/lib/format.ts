export function formatPrice(cents: number): string {
	return `$${(cents / 100).toLocaleString('en-US', { maximumFractionDigits: 2 })}`;
}

export function timeAgo(iso: string): string {
	const seconds = Math.max(1, (Date.now() - new Date(iso).getTime()) / 1000);
	if (seconds < 60) return 'just now';
	const minutes = seconds / 60;
	if (minutes < 60) return `${Math.floor(minutes)}m ago`;
	const hours = minutes / 60;
	if (hours < 24) return `${Math.floor(hours)}h ago`;
	const days = hours / 24;
	if (days < 7) return `${Math.floor(days)}d ago`;
	const weeks = days / 7;
	if (weeks < 5) return `${Math.floor(weeks)}w ago`;
	const months = days / 30;
	if (months < 12) return `${Math.floor(months)}mo ago`;
	return `${Math.floor(days / 365)}y ago`;
}

export const CONDITION_LABEL: Record<string, string> = {
	like_new: 'Like new',
	good: 'Good',
	fair: 'Fair'
};

export const CATEGORY_COLORS: Record<string, string> = {
	bikes: 'var(--keep-blue)',
	furniture: 'var(--keep-green)',
	electronics: 'var(--keep-orange)',
	instruments: 'var(--keep-pink)',
	books: 'var(--keep-brown)',
	sports: 'var(--keep-red)',
	other: 'var(--keep-teal)'
};

export function categoryColor(category: string): string {
	return CATEGORY_COLORS[category.toLowerCase()] ?? CATEGORY_COLORS.other;
}

export function categoryLabel(category: string): string {
	const key = category.toLowerCase();
	const labels: Record<string, string> = {
		bikes: 'Bikes',
		furniture: 'Furniture',
		electronics: 'Electronics',
		instruments: 'Musical instruments',
		books: 'Books & comics',
		sports: 'Sports',
		other: 'Other'
	};
	return labels[key] ?? category;
}
