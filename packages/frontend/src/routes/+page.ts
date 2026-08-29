import { error } from '@sveltejs/kit';
import { api, ApiError } from '$lib/api';
import type { BrowseParams } from '$lib/types';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url, depends }) => {
	depends('vdl:browse');

	const q = url.searchParams.get('q') ?? '';
	const category = url.searchParams.get('category') ?? 'all';
	const status = (url.searchParams.get('status') as BrowseParams['status']) ?? 'active';
	const sort = (url.searchParams.get('sort') as BrowseParams['sort']) ?? 'recent';

	try {
		const listings = await api.browse({ q, category, status, sort });
		return { listings, q, category, status, sort };
	} catch (e) {
		if (e instanceof ApiError && e.status === 404) error(404, 'Not found');
		throw e;
	}
};
