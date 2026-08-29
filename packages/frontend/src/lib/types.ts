export type ListingStatus = 'active' | 'sold' | 'withdrawn';

export interface UserPublic {
	handle: string;
	name: string;
	bio: string;
	avatar_color: string;
	created_at: string;
	trust_score: number;
	positive_pct: number;
	sales_count: number;
	flags_upheld: number;
	verified: boolean;
}

export type EventKind =
	| 'listed'
	| 'price_drop'
	| 'price_raise'
	| 'description_edited'
	| 'photo_added'
	| 'verified'
	| 'sold'
	| 'withdrawn'
	| 'relisted'
	| 'conversation_public';

export interface ListingEvent {
	id: number;
	listing_id: number;
	kind: EventKind;
	summary: string;
	detail: string | null;
	hash: string;
	created_at: string;
}

export interface Listing {
	id: number;
	title: string;
	description: string;
	price_cents: number;
	previous_price_cents: number | null;
	condition: 'like_new' | 'good' | 'fair';
	status: ListingStatus;
	category: string;
	location: string;
	image_url: string | null;
	seller: UserPublic;
	created_at: string;
	updated_at: string;
	sold_at: string | null;
	event_count: number;
	last_event: { kind: EventKind; summary: string; created_at: string } | null;
	public_conversation_count: number;
	open_conversation_count: number;
}

export interface ConversationMessage {
	id: number;
	author_handle: string;
	author_name: string;
	body: string;
	created_at: string;
}

export interface Conversation {
	id: number;
	listing_id: number;
	buyer_handle: string;
	buyer_name: string;
	is_public: boolean;
	created_at: string;
	message_count: number;
	last_message_at: string | null;
}

export interface ConversationDetail extends Conversation {
	messages: ConversationMessage[];
}

export interface Rating {
	id: number;
	listing_id: number;
	rater_handle: string;
	ratee_handle: string;
	stars: number;
	text: string;
	created_at: string;
}

export interface ListingDetail extends Listing {
	events: ListingEvent[];
	conversations: Conversation[];
	similar: Listing[];
	my_rating: {
		id: number;
		stars: number;
		text: string;
		ratee_handle: string;
		created_at: string;
	} | null;
}

export interface BrowseParams {
	q?: string;
	category?: string;
	status?: 'active' | 'sold' | 'all';
	sort?: 'recent' | 'price_asc' | 'price_desc' | 'events';
}
