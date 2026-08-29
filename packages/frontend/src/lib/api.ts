import type {
	BrowseParams,
	Conversation,
	ConversationDetail,
	ConversationMessage,
	Listing,
	ListingDetail,
	ListingEvent,
	Rating,
	UserPublic
} from '$lib/types';

export class ApiError extends Error {
	constructor(
		public status: number,
		message: string
	) {
		super(message);
	}
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
	const headers = new Headers(init?.headers);
	if (init?.body !== undefined) headers.set('Content-Type', 'application/json');
	const res = await fetch(`/api${path}`, { ...init, headers });
	if (!res.ok) {
		let detail = res.statusText;
		try {
			const body = await res.json();
			if (typeof body.detail === 'string') detail = body.detail;
		} catch {
			/* non-JSON error body */
		}
		throw new ApiError(res.status, detail);
	}
	if (res.status === 204) return undefined as T;
	return (await res.json()) as T;
}

export const api = {
	health: () => request<{ status: string }>('/health'),

	me: () => request<UserPublic | null>('/me'),
	users: () => request<UserPublic[]>('/users'),

	register: (body: { handle: string; name: string; password: string }) =>
		request<UserPublic>('/auth/register', { method: 'POST', body: JSON.stringify(body) }),

	login: (body: { handle: string; password: string }) =>
		request<UserPublic>('/auth/login', { method: 'POST', body: JSON.stringify(body) }),

	logout: () => request<{ ok: boolean }>('/auth/logout', { method: 'POST' }),

	browse: (params: BrowseParams = {}) => {
		const qs = new URLSearchParams();
		if (params.q) qs.set('q', params.q);
		if (params.category && params.category !== 'all') qs.set('category', params.category);
		if (params.status) qs.set('status', params.status);
		if (params.sort) qs.set('sort', params.sort);
		const suffix = qs.toString() ? `?${qs.toString()}` : '';
		return request<Listing[]>(`/listings${suffix}`);
	},

	listing: (id: number) => request<ListingDetail>(`/listings/${id}`),

	createListing: (body: {
		title: string;
		description: string;
		price: number;
		condition: string;
		category: string;
		location: string;
		image_url?: string;
	}) =>
		request<Listing>('/listings', {
			method: 'POST',
			body: JSON.stringify(body)
		}),

	updateListing: (
		id: number,
		body: { title?: string; description?: string; price?: number; location?: string }
	) =>
		request<Listing>(`/listings/${id}`, {
			method: 'PATCH',
			body: JSON.stringify(body)
		}),

	changeStatus: (id: number, action: 'sold' | 'withdrawn' | 'active') =>
		request<Listing>(`/listings/${id}/status`, {
			method: 'POST',
			body: JSON.stringify({ action })
		}),

	listingEvents: (id: number) => request<ListingEvent[]>(`/listings/${id}/events`),

	conversations: (listingId: number) =>
		request<Conversation[]>(`/listings/${listingId}/conversations`),

	startConversation: (listingId: number, body: string) =>
		request<Conversation>(`/listings/${listingId}/conversations`, {
			method: 'POST',
			body: JSON.stringify({ body })
		}),

	conversation: (id: number) => request<ConversationDetail>(`/conversations/${id}`),

	sendMessage: (id: number, body: string) =>
		request<ConversationMessage>(`/conversations/${id}/messages`, {
			method: 'POST',
			body: JSON.stringify({ body })
		}),

	unhideConversation: (id: number) =>
		request<Conversation>(`/conversations/${id}/unhide`, { method: 'POST' }),

	user: (handle: string) => request<UserPublic>(`/users/${handle}`),

	userListings: (handle: string) => request<Listing[]>(`/users/${handle}/listings`),

	userRatings: (handle: string, direction: 'received' | 'given') =>
		request<Rating[]>(`/users/${handle}/ratings?direction=${direction}`),

	rate: (listingId: number, stars: number, text: string) =>
		request<Rating>('/ratings', {
			method: 'POST',
			body: JSON.stringify({ listing_id: listingId, stars, text })
		}),

	flagUser: (handle: string, reason: string) =>
		request<{ ok: boolean }>('/flags', {
			method: 'POST',
			body: JSON.stringify({ handle, reason })
		})
};
