export const POST = async ({ request }) => {
  const body = await request.json();
  const listName = await body.name;
};
