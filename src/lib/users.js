import { AccountCollection, SavedLists } from "./db";

const getAccountCollection = async () => {
  return await AccountCollection();
};

const getSavedListsCollection = async () => {
  return await SavedLists();
};

export const createAccount = async (newAccount) => {
  try {
    const collection = await getAccountCollection();
    console.log("connection received");
    const result = await collection.insertMany(newAccount);
    return result;
  } catch (error) {
    console.error("Error creating account:", error.message);
    throw new Error("Failed to create account.", error);
  }
};

export const getAccountHolders = async (page) => {
  try {
    const pageSize = 24;
    const skipCount = (page - 1) * pageSize;
    const collection = await getAccountCollection();
    const totalItems = await collection.countDocuments();

    const data = await collection
      .find({}, { projection: { CNumber: 0 } })
      // .sort({ _id: -1 })
      .skip(skipCount)
      .limit(pageSize)
      .toArray();
    return {
      totalItems,
      totalPages: Math.ceil(totalItems / pageSize),
      accounts: data,
      totalItems: totalItems,
    };
  } catch (err) {
    console.log("Error Fetching accounts", err.message);
  }
};

export const checkForActiveList = async () => {
  try {
    const collection = await getSavedListsCollection();
    const activeListId = await collection
      .find({ active: true }, { projection: { _id: 1, listName: 1 } })
      .toArray();
    return activeListId;
  } catch (err) {
    console.log("Error Fetching saved lists", err.message);
  }
};

export const createList = async (doc) => {
  try {
    const collection = await getSavedListsCollection();
    const insertList = await collection.insertMany(doc);
    return insertList;
  } catch (err) {
    console.log("Error creating list", err.message);
  }
};

export const setActiveList = async (id) => {
  try {
    const collection = await getSavedListsCollection();
    const setActive = await collection.bulkWrite([
      {
        updateMany: {
          filter: { active: true },
          update: { $set: { active: false } },
        },
      },
      {
        updateOne: {
          filter: { listName: id },
          update: { $set: { active: true } },
        },
      },
    ]);
    return setActive;
  } catch (err) {
    "Error While activating list", err.message;
  }
};

export const AddToActiveList = async (account) => {
  const activeList = await checkForActiveList();
  const listCollection = await getSavedListsCollection();
  try {
    listCollection.updateOne(
      { _id: { $oid: activeList[0]._id } },
      { $push: { accounts: account } }
    );
  } catch (err) {
    console.log(err.message);
  }
  const accountCollection = await getAccountCollection();
  try {
    await accountCollection.updateOne(
      { _id: { $oid: account } },
      { $addToSet: { addedIn: { $oid: activeList[0]._id } } }
    );
  } catch (err) {
    console.log(err.message);
  }
};
