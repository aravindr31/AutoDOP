import { checkForActiveList, setActiveList } from "../../../../lib/users";

export const GET = async () => {
  const id = await checkForActiveList();
  if (!id) {
    return new Response(null, {
      status: 404,
      statusText: "Not found",
    });
  }
  if (id.length != 0)
    return new Response(JSON.stringify(id[0]), {
      status: 200,
    });
  return new Response(JSON.stringify({}), {
    status: 200,
  });
};

export const POST = async ({ request }) => {
  const body = await request.json();
  const listName = await body.name;

  if (typeof listName === "string" && /^[A-Z]$/.test(listName)) {
    if (!listName) {
      return new Response(null, {
        status: 404,
        statusText: "Not found",
      });
    }

    const activateList = await setActiveList(listName);
    return new Response(JSON.stringify(activateList), {
      status: 200,
    });
  }
};
