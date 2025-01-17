import { createList } from "../../../../lib/users";
export const POST = async () => {
  let data = [];
  for (let i = 65; i <= 90; i++) {
    data.push({
      listName: String.fromCharCode(i),
      active: false,
      accounts: [],
    });
  }

  const dataAdded = await createList(data);

  return new Response(JSON.stringify(dataAdded), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
};
