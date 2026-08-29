import { error } from '@sveltejs/kit';
import { api, ApiError } from '$lib/api';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, depends }) => {
	depends('vdl:session');

	try {
		const [user, listings, ratings] = await Promise.all([
			api.user(params.handle),
			api.userListings(params.handle),
			api.userRatings(params.handle, 'received')
		]);
		return { user, listings, ratings };
	} catch (e) {
		if (e instanceof ApiError && e.status === 404) error(404, `No user @${params.handle}`);
		throw e;
	}
};
