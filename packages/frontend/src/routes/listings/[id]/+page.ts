import { error } from '@sveltejs/kit';
import { api, ApiError } from '$lib/api';
import type { ConversationDetail } from '$lib/types';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, depends }) => {
	depends('vdl:session');

	try {
		const listing = await api.listing(Number(params.id));
		const details: Record<number, ConversationDetail> = {};
		await Promise.all(
			listing.conversations.map(async (conversation) => {
				details[conversation.id] = await api.conversation(conversation.id);
			})
		);
		return { listing, conversationDetails: details };
	} catch (e) {
		if (e instanceof ApiError && e.status === 404) error(404, 'This listing does not exist');
		throw e;
	}
};
