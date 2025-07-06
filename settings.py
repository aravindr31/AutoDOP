import streamlit as st
from bson import ObjectId

def decrypt_dop_passwd(fernet,password):
    return fernet.decrypt(password).decode()

def verify_password(fernet,password,current_password):
    decrypted_passswd = fernet.decrypt(password).decode()

    if decrypted_passswd == current_password:
        return True
    return False

def update_password(fernet,user_id,new_password,userCollection):

    encrypted_passwd = fernet.encrypt(new_password.encode())
    userCollection.update_one(
    {"_id": ObjectId(user_id)}, 
    {"$set": {"UserInfo.DOP_password": encrypted_passwd.decode()}} 
)
    
    return True

def show_password_change_form(fernet,userInfo,userCollection):
    st.header("🔑 Change DOP Password")

    if "logged_in" in st.session_state and st.session_state.logged_in:

        with st.form("password_change_form"):
            current_password = st.text_input("🔒 Current Password", type="password")
            new_password = st.text_input("🆕 New Password", type="password")
            confirm_password = st.text_input("✅ Confirm New Password", type="password")
            
            submit = st.form_submit_button("Update Password")

            if submit:
                if not verify_password(fernet,userInfo[0]["UserInfo"]["DOP_password"],current_password):
                    st.error("❌ Incorrect current password.")
                elif new_password != confirm_password:
                    st.error("❌ New passwords do not match.")
                elif len(new_password) < 6:
                    st.warning("⚠ Password must be at least 6 characters long.")
                else:
                    update_password(fernet,userInfo[0]["_id"],new_password,userCollection)
                    st.success("✅ Password updated successfully!")

    else:
        st.warning("❌ Please log in to change your password.")

def new_account(collection,name, account_number, cnumber, ref_number, denomination):
    """Add a new account to MongoDB."""
    new_account = {
        "Name": name,
        "Number": account_number,
        "CNumber": cnumber,
        "Ref_Number": ref_number,
        "Denomination": denomination,
        "addedIn":""

    }

    result = collection.insert_one(new_account)
    return result.inserted_id

def show_add_new_account_form(account_collection):
    st.title("➕ Add New Account")

    with st.form("add_account_form"):
        st.subheader("👤 Account Details")
        name = st.text_input("Full Name")
        account_number = st.text_input("Account Number")
        cnumber = st.text_input("CNumber")
        ref_number = st.text_input("Ref Number")
        denomination = st.text_input("Denomination")

        submit = st.form_submit_button("Create Account")

        if submit:
            if not name or not account_number or not cnumber or not ref_number or not denomination:
                st.error("❌ All fields are required!")
            elif not denomination.isdigit():
                st.error("❌ Amount and Denomination must be numbers!")
            else:
                account_id = new_account(account_collection,name, account_number, cnumber, ref_number, int(denomination))
                st.success(f"✅ Account created successfully! (ID: {account_id})")

def delete_account(collection, account_number):
    result = collection.delete_one({"Number": account_number})

    if result.deleted_count > 0:
        return True
    return False

def show_delete_account_form(collection):
    st.title("🗑 Delete Account")

    with st.form("delete_account_form"):
        st.subheader("⚠ Enter Account Number to Delete")
        account_number = st.text_input("Account Number")

        submit = st.form_submit_button("Delete Account")

        if submit:
            if not account_number:
                st.error("❌ Account Number is required!")
            else:
                success = delete_account(collection,account_number)
                if success:
                    st.success(f"✅ Account {account_number} deleted successfully!")
                else:
                    st.warning(f"⚠ Account {account_number} not found!")

def update_account(collection, account_number, updates):
    """Update an existing account in MongoDB."""
    result = collection.update_one(
        {"Number": account_number},
        {"$set": updates}
    )
    return result.modified_count > 0

def show_update_account_form(collection):
    st.title("✏️ Update Account")

    # First, let user search for the account
    account_number = st.text_input("🔍 Enter Account Number to Update")
    
    if account_number:
        # Find the account
        account = collection.find_one({"Number": account_number})
        
        if account:
            st.success("✅ Account found! Update the details below:")
            
            with st.form("update_account_form"):
                st.subheader("📝 Update Account Details")
                
                # Pre-fill the form with existing values
                name = st.text_input("Full Name", value=account.get("Name", ""))
                new_account_number = st.text_input("Account Number", value=account.get("Number", ""))
                cnumber = st.text_input("CNumber", value=account.get("CNumber", ""))
                ref_number = st.text_input("Ref Number", value=account.get("Ref_Number", ""))
                denomination = st.text_input("Denomination", value=str(account.get("Denomination", "")))

                submit = st.form_submit_button("Update Account")

                if submit:
                    if not name or not new_account_number or not cnumber or not ref_number or not denomination:
                        st.error("❌ All fields are required!")
                    elif not denomination.isdigit():
                        st.error("❌ Denomination must be a number!")
                    else:
                        updates = {
                            "Name": name,
                            "Number": new_account_number,
                            "CNumber": cnumber,
                            "Ref_Number": ref_number,
                            "Denomination": int(denomination)
                        }
                        
                        if update_account(collection, account_number, updates):
                            st.success("✅ Account updated successfully!")
                        else:
                            st.error("❌ Failed to update account. Please try again.")
        else:
            st.error("❌ Account not found!")