import { getAccountHolders } from "../../../../lib/users";

export const GET = async ({ request }) => {
  const reqUrl = new URL(request.url);
  const page = reqUrl.searchParams.get("page") || 1;
  const accounts = await getAccountHolders(page);
  if (!accounts) {
    return new Response(null, {
      status: 404,
      statusText: "Not found",
    });
  }

  return new Response(JSON.stringify(accounts), {
    status: 200,
  });
};
