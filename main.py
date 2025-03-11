import streamlit as st
import pymongo
from bson import ObjectId
import pyperclip
import subprocess
import os
import bcrypt
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import settings
import hashlib
from datetime import datetime, timedelta
import json
# Load environment variables once at startup
load_dotenv(".env.local")

# Configuration constants
KEY = os.getenv("FERNET_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
MONGO_URI = os.getenv("MONGO_URI")

# Initialize encryption once
fernet = Fernet(KEY.encode())

# Set page config 
st.set_page_config(layout="wide", page_title="AutoDOP")

# Create a directory to store session files
SESSION_DIR = os.path.join(os.getcwd(), ".sessions")
if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)

def get_session_id():
    """Generate a session ID from browser metadata"""
    user_agent = os.environ.get("HTTP_USER_AGENT", "")
    ip_address = os.environ.get("REMOTE_ADDR", "")
    # Create a unique session ID based on user agent and IP
    session_key = f"{user_agent}:{ip_address}"
    return hashlib.md5(session_key.encode()).hexdigest()

def load_session():
    """Load session data if it exists"""
    if "session_id" not in st.session_state:
        st.session_state.session_id = get_session_id()
    
    session_path = os.path.join(SESSION_DIR, f"{st.session_state.session_id}.json")
    
    if os.path.exists(session_path):
        try:
            with open(session_path, "r") as f:
                session_data = json.load(f)
            
            # Check if session is expired
            expiry = datetime.fromisoformat(session_data.get("expiry", "2000-01-01"))
            if expiry > datetime.now():
                # Session is valid, load data into session state
                for key, value in session_data.get("data", {}).items():
                    st.session_state[key] = value
                return True
            else:
                # Session expired, delete file
                os.remove(session_path)
        except Exception as e:
            print(f"Error loading session: {e}")
    
    return False

def save_session(days=7):
    """Save session data to file"""
    session_data = {
        "expiry": (datetime.now() + timedelta(days=days)).isoformat(),
        "data": {
            "logged_in": st.session_state.get("logged_in", False),
            "username": st.session_state.get("username", "")
        }
    }
    
    session_path = os.path.join(SESSION_DIR, f"{st.session_state.session_id}.json")
    
    try:
        with open(session_path, "w") as f:
            json.dump(session_data, f)
    except Exception as e:
        print(f"Error saving session: {e}")

def clear_session():
    """Clear the session file"""
    session_path = os.path.join(SESSION_DIR, f"{st.session_state.session_id}.json")
    if os.path.exists(session_path):
        os.remove(session_path)

# MongoDB Connection
@st.cache_resource
def get_mongo_client():
    return pymongo.MongoClient(MONGO_URI)

client = get_mongo_client()
db = client["accounts"]
collection = db["accountHolders"]
list_collection = db["savedList"]
user_collection = db["users"]

@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_user_creds():
    return list(user_collection.aggregate([
        {
            "$match": {"_id": ObjectId("5fbf919c87da8228f87bd62f")},
        },
        {
            "$project": {
                "_id": 1,
                "username": 1,
                "password": 1,
                "UserInfo": {
                    "DOP_ID": 1,
                    "DOP_password": 1,
                },
            },
        },
    ]))

def decrypt_dop_cred(encrypted_pass):
    return fernet.decrypt(encrypted_pass).decode()

# Fetch data from MongoDB with caching
@st.cache_data(ttl=60)  # Cache for 1 minute
def get_data():
    return list(collection.find(
        {}, 
        {"_id": 1, "Number": 1, "Name": 1, "Denomination": 1, "CNumber": 1, "Ref_Number": 1, "addedIn": 1}
    ))

@st.cache_data(ttl=60)  # Cache for 1 minute
def get_lists():
    return list(list_collection.find({}, {"_id": 1, "listName": 1, "active": 1, "accounts": 1}))

def update_list_status(list_id, is_active):
    # collections = get_db_collections()
    try:
        # If setting a list to active, first deactivate all other lists
        if is_active:
            list_collection.update_many(
                {"_id": {"$ne": ObjectId(list_id)}},
                {"$set": {"active": False}}
            )
        
        # Update the specified list
        list_collection.update_one(
            {"_id": ObjectId(list_id)},
            {"$set": {"active": is_active}}
        )
        
        # Clear cache to reflect changes
        get_lists.clear()
        return True
    except Exception as e:
        st.error(f"Error updating list status: {e}")
        return False

def update_list(record_id, selected_list_id, selected_list_name):
    # Update the list document
    list_collection.update_one(
        {"_id": ObjectId(selected_list_id)}, 
        {"$addToSet": {"accounts": {"id": ObjectId(record_id), "rebate": 1}}}
    )
    
    # Update the collection document
    collection.update_one(
        {"_id": ObjectId(record_id)}, 
        {"$set": {"addedIn": selected_list_name}}
    )
    st.success("Added to selected list")
    # Clear cached data after update
    get_data.clear()
    get_lists.clear()
    get_lists_with_accounts.clear()

def remove_from_list(record_id):
    # Fetch the list name from the collection
    record = collection.find_one({"_id": ObjectId(record_id)}, {"addedIn": 1})
    if record and record.get("addedIn"):
        list_name = record["addedIn"]
        
        # Remove the item from the list document
        list_collection.update_one(
            {"listName": list_name}, 
            {"$pull": {"accounts": {"id": ObjectId(record_id)}}}
        )
        
        # Remove the list name from the collection document
        collection.update_one(
            {"_id": ObjectId(record_id)}, 
            {"$set": {"addedIn": ""}}
        )
        st.success("Removed from selected list")
        # Clear cached data after update
        get_data.clear()
        get_lists.clear()
        get_lists_with_accounts.clear()

@st.cache_data(ttl=60)  # Cache for 1 minute
def get_lists_with_accounts():
    pipeline = [
        {
            "$unwind": {"path": "$accounts", "preserveNullAndEmptyArrays": False}
        },
        {
            "$lookup": {
                "from": "accountHolders",
                "localField": "accounts.id",
                "foreignField": "_id",
                "as": "account_details"
            }
        },
        {
            "$unwind": "$account_details"
        },
        {
            "$addFields": {
                "account_details.Rebate": "$accounts.rebate",
                "account_details.Denomination": {
                    "$convert": {
                        "input": "$account_details.Denomination",
                        "to": "int",
                        "onError": "$account_details.Denomination"
                    }
                }
            }
        },
        {
            "$group": {
                "_id": "$_id",
                "listName": {"$first": "$listName"},
                "total_count": {"$sum": 1},
                "total_amount": {"$sum": "$account_details.Denomination"},
                "account_details": {"$push": "$account_details"}
            }
        }
    ]
    return list(list_collection.aggregate(pipeline))

def update_rebate(list_id, record_id, new_rebate):
    try:
        result = list_collection.update_one(
            {
                "_id": ObjectId(list_id),
                "accounts.id": ObjectId(record_id)
            },
            {
                "$set": {"accounts.$.rebate": new_rebate}
            }
        )

        if result.modified_count > 0:
            st.success(f"Rebate updated to {new_rebate}")
            
            # Clear cache after update
            get_lists_with_accounts.clear()
            get_updated_list.clear()
            
            # Update session state
            st.session_state[f"list_{list_id}"] = get_updated_list(list_id) or {}
            st.rerun()
        else:
            st.warning("Rebate update failed. Check if the record exists.")

    except Exception as e:
        st.error(f"Error updating rebate: {e}")

@st.cache_data(ttl=30)  # Short cache for dynamic content
def get_updated_list(_list_id):
    pipeline = [
        {"$match": {"_id": ObjectId(_list_id)}},
        {"$unwind": {"path": "$accounts", "preserveNullAndEmptyArrays": True}},
        {
            "$lookup": {
                "from": "accountHolders",
                "localField": "accounts.id",
                "foreignField": "_id",
                "as": "account_details"
            }
        },
        {"$unwind": {"path": "$account_details", "preserveNullAndEmptyArrays": True}},
        {
            "$addFields": {
                "account_details.Rebate": {
                    "$ifNull": [
                        {"$convert": {
                            "input": "$accounts.rebate",
                            "to": "int",
                            "onError": "$accounts.rebate"
                        }},
                        0
                    ]
                },
                "account_details.Denomination": {
                    "$convert": {
                        "input": "$account_details.Denomination",
                        "to": "int",
                        "onError": "$account_details.Denomination"
                    }
                }
            }
        },
        {
            "$addFields": {
                "account_details.TotalAmount": {
                    "$multiply": ["$account_details.Denomination", "$account_details.Rebate"]
                }
            }
        },
        {
            "$group": {
                "_id": "$_id",
                "listName": {"$first": "$listName"},
                "total_count": {"$sum": {"$cond": [{"$ifNull": ["$account_details._id", False]}, 1, 0]}},
                "total_amount": {"$sum": {"$ifNull": ["$account_details.TotalAmount", 0]}},
                "account_details": {
                    "$push": {
                        "$cond": [
                            {"$ifNull": ["$account_details._id", False]},
                            "$account_details",
                            "$$REMOVE"
                        ]
                    }
                }
            }
        }
    ]

    updated_list = list(list_collection.aggregate(pipeline))
    return updated_list[0] if updated_list else {}

def purge_list(list_id):
    try:
        # Fetch all account IDs before purging the list
        list_doc = list_collection.find_one({"_id": ObjectId(list_id)}, {"accounts": 1})
        if not list_doc or "accounts" not in list_doc:
            st.warning("No accounts found in the list.")
            return

        account_ids = [acc["id"] for acc in list_doc["accounts"]]

        # Update all accounts to remove addedIn field
        if account_ids:
            collection.update_many(
                {"_id": {"$in": account_ids}},
                {"$set": {"addedIn": ""}}
            )

        # Clear the accounts array in the list
        result = list_collection.update_one(
            {"_id": ObjectId(list_id)},
            {"$set": {"accounts": []}}
        )

        if result.modified_count > 0:
            st.success("All accounts removed from the list and `addedIn` fields reset!")
            
            # Clear all relevant caches
            get_data.clear()
            get_lists.clear()
            get_lists_with_accounts.clear()
            get_updated_list.clear()
            
            st.rerun()
        else:
            st.warning("Failed to purge the list.")

    except Exception as e:
        st.error(f"Error purging list: {e}")

def run_scraper_script(username, passwd,lists_data):
    script_path = os.path.join(os.getcwd(), "scraper.py")
    try:
        # Capture the output with subprocess.run
        result = subprocess.run(
            ["python3", script_path, username, passwd, lists_data],
            check=True,
            text=True,
            capture_output=True
        )
        return result
    except subprocess.CalledProcessError as e:
        st.error(f"Error running script: {e}")

def check_login(username, password):
    user_creds = get_user_creds()
    if not user_creds:
        return False
        
    if username == user_creds[0]["username"] and bcrypt.checkpw(
        password.encode(), user_creds[0]["password"].encode()
    ):
        return True
    return False

def login_page():
    st.title("🔑 Login Page")
    
    # Check if already logged in via session state
    if st.session_state.get("logged_in", False):
        st.success(f"✅ Welcome, {st.session_state.username}!")
        return
    
    # Login form
    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")
    
    if st.button("Login"):
        if check_login(username, password):
            # Set session state
            st.session_state.logged_in = True
            st.session_state.username = username
            
            # Save session to file
            save_session()
            
            st.success(f"✅ Welcome, {username}!")
            st.rerun()
        else:
            st.error("❌ Invalid username or password.")

def account_view():
    st.title("AutoDOP")
    
    # Get and cache lists
    # Get and cache lists
    lists = get_lists()
    if not lists:
        st.warning("No lists available. Please create a list first.")
        return

    # Find the active list
    active_list = next((lst for lst in lists if lst.get("active", False)), None)

    # If no active list is found, use the first list or the one in session state
    if not active_list:
        selected_list = st.session_state.get("selected_list", str(lists[0]["_id"]) if lists else None)
    else:
        # Use the active list
        selected_list = str(active_list["_id"])
        # Update session state
        st.session_state.selected_list = selected_list

    selected_list_data = next((l for l in lists if str(l["_id"]) == selected_list), None)

    # List selection UI
    st.write("### Select Active List")
    cols = st.columns(len(lists))
    for i, lst in enumerate(lists):
        # Show currently active list with different styling
        is_active = str(lst["_id"]) == selected_list
        button_label = f"{lst['listName']}" if is_active else lst["listName"]
        
        if cols[i].button(button_label, key=f"list_{lst['_id']}", type="primary" if is_active else "secondary"):
            # Update the previous active list to inactive
            if selected_list_data and selected_list_data.get("active", False):
                update_list_status(str(selected_list_data["_id"]), False)
                
            # Set the new list as active
            update_list_status(str(lst["_id"]), True)
            
            # Update session state
            st.session_state.selected_list = str(lst["_id"])
            selected_list = str(lst["_id"])
            selected_list_data = lst
            
            # Refresh the page
            st.rerun()

    # Display active list name with highlighting
    if selected_list_data:
        st.markdown(f"**Active List: <span style='color:#FF4B4B;'>{selected_list_data['listName']}</span>**", unsafe_allow_html=True)
    else:
        st.write("**Active List: None**")

    st.divider()

    # Search interface
    search_query = st.text_input("**Search Accounts**")
    st.divider()

    # Data fetching and filtering
    data = get_data()
    if search_query:
        data = [row for row in data if search_query.lower() in str(row.get("Ref_Number", "")).lower()]

    # Display data table
    if not data:
        st.warning("No results found.")
        return
        
    if not selected_list_data:
        st.warning("No active list selected.")
        return
    
    # Create a container for scrollable content
    with st.container():
        # Table headers
        # header_cols = st.columns([2, 3, 2, 3, 2, 2])
        # header_cols[0].write("**Number**")
        # header_cols[1].write("**Name**")
        # header_cols[2].write("**Denomination**")
        # header_cols[3].write("**CNumber**")
        # header_cols[4].write("**Action**")
        # header_cols[5].write("**Remove**")
        
        # st.divider()
        
        # Table rows
        for row in data:
            cols = st.columns([2, 3, 2, 3, 2, 2])
            cols[0].write(row.get("Number", ""))
            cols[1].write(row.get("Name", ""))
            cols[2].write(row.get("Denomination", ""))
            cols[3].write(row.get("CNumber", ""))
            
            row_id_str = str(row["_id"])
            is_added = row.get("addedIn", "") != ""
            button_text = f"Added to {row.get('addedIn', '')}" if is_added else "Add to List"
            
            if cols[4].button(button_text, key=f"add_{row_id_str}", disabled=is_added):
                update_list(row_id_str, selected_list, selected_list_data["listName"])
                st.rerun()

            if is_added and cols[5].button("Delete", key=f"del_{row_id_str}", type="primary"):
                remove_from_list(row_id_str)
                st.rerun()

def list_view():
    st.title("List View")
    lists = get_lists_with_accounts()

    if not lists:
        st.warning("No lists with accounts found.")
    
        return
    # Sort lists by listName in ascending order
    lists = sorted(lists, key=lambda x: x.get('listName', '').lower())
    
    # Add a "Generate All Lists" button at the top
    if st.button("📄 Generate All Lists", type="primary"):
        with st.spinner("Preparing all lists for processing..."):
            try:
                user_creds = get_user_creds()
                if not user_creds:
                    st.error("User credentials not found")
                else:
                    # Prepare lists data
                    lists_data = []
                    for lst in lists:
                        account_details = lst.get("account_details", [])
                        numbers = [acc.get("Number", "") for acc in account_details]
                        rebate_values = [acc.get("Rebate", 0) for acc in account_details]
                        
                        lists_data.append({
                            "name": lst['listName'],
                            "numbers": numbers,
                            "rebate": rebate_values
                        })
                    
                    # Convert to JSON for passing to the script
                    lists_json = json.dumps(lists_data)
                    
                    # Get credentials
                    decrypted_password = settings.decrypt_dop_passwd(fernet, user_creds[0]["UserInfo"]["DOP_password"])
                    username = user_creds[0]["UserInfo"]["DOP_ID"]
                    
                    result = run_scraper_script(username, decrypted_password, lists_json)
                    
                    # Process results
                    if result.stdout:
                        try:
                            results = json.loads(result.stdout)
                            
                            # Display results
                            st.subheader("List Generation Results")
                            for result_item in results:
                                if result_item.get("status") == "success":
                                    st.success(f"List '{result_item.get('list_name')}' generated successfully!")
                                    with st.expander(f"Details for {result_item.get('list_name')}"):
                                        st.json(result_item.get("details", {}))
                                else:
                                    st.error(f"Error processing list '{result_item.get('list_name')}': {result_item.get('details')}")
                        except json.JSONDecodeError:
                            st.code(result.stdout)
                            st.warning("Could not parse script output as JSON")
                    
                    if result.stderr:
                        st.error("Errors occurred during processing:")
                        st.code(result.stderr)
            except Exception as e:
                st.error(f"Error generating lists: {str(e)}")

    # The rest of your original code for displaying individual lists
    for lst in lists:
        # Get list data from session state or fetch it
        list_data = st.session_state.get(f"list_{lst['_id']}", lst)
        if not isinstance(list_data, dict):
            list_data = lst

        total_count = list_data.get("total_count", 0)
        total_amount = list_data.get("total_amount", 0)

        with st.expander(f"List: {list_data.get('listName', 'Unknown')}", expanded=True):
            account_details = list_data.get("account_details", [])
            st.markdown(f"**Total Accounts:** {total_count}  |  **Total Amount:** {total_amount}")

            if account_details:
                # Table headers
                header_cols = st.columns([2, 3, 2, 2, 1, 1, 2])
                header_cols[0].write("**Number**")
                header_cols[1].write("**Name**")
                header_cols[2].write("**Denomination**")
                header_cols[3].write("**CNumber**")
                header_cols[5].write("**Rebate**")
                header_cols[6].write("**Action**")

                
                st.divider()
                
                # Account rows
                for account in account_details:
                    row_id_str = str(account.get("_id", ""))
                    rebate_value = account.get("Rebate", 0)

                    cols = st.columns([2, 3, 2, 2, 1, 1, 2])
                    cols[0].write(account.get("Number", ""))
                    cols[1].write(account.get("Name", ""))
                    cols[2].write(str(account.get("Denomination", "")))
                    # cols[3].write(str(account.get("CNumber", "")))

                    # Rebate controls
                    if cols[3].button("➖", key=f"dec_{row_id_str}"):
                        update_rebate(lst["_id"], row_id_str, max(rebate_value - 1, 0))
                    
                    cols[4].write(rebate_value)

                    if cols[5].button("➕", key=f"inc_{row_id_str}"):
                        update_rebate(lst["_id"], row_id_str, rebate_value + 1)
                    
                    if cols[6].button("Delete", key=f"del_{row_id_str}", type="primary"):
                        remove_from_list(row_id_str)
                        st.rerun()
            else:
                st.write("List is empty.")

            st.divider()
            
            # Action buttons - KEEP THIS ORIGINAL STRUCTURE
            with st.container():
                center_cols = st.columns([1, 3, 1])
                with center_cols[1]:
                    action_cols = st.columns(3)
                    
                    # Numbers and rebate data
                    numbers = [acc.get("Number", "") for acc in account_details]
                    rebate_data = [acc.get("Rebate", 0) for acc in account_details]
                    
                    # Copy numbers button (keep this from original code)
                    if action_cols[0].button("📋 Copy Numbers", key=f"copy_{lst['_id']}"):
                        st.session_state[f"copied_text_{lst['_id']}"] = ", ".join(numbers)

                    if f"copied_text_{lst['_id']}" in st.session_state:
                        move_to_clipboard = st.text_area(
                            "Copied Numbers",
                            st.session_state[f"copied_text_{lst['_id']}"],
                            disabled=True,
                            height=68
                        )
                        pyperclip.copy(move_to_clipboard)
                        st.success("Numbers copied!")

                    # MODIFY THE GENERATE LIST BUTTON TO USE NEW APPROACH
                    if action_cols[1].button("📄 Generate List", key=f"generate_{lst['_id']}"):
                        try:
                            user_creds = get_user_creds()
                            if user_creds:
                                decrypted_password = settings.decrypt_dop_passwd(fernet, user_creds[0]["UserInfo"]["DOP_password"])
                                
                                # Prepare a single list for processing
                                single_list_data = [{
                                    "name": lst['listName'],
                                    "numbers": numbers,
                                    "rebate": rebate_data
                                }]
                                
                                lists_json = json.dumps(single_list_data)
                                
                                result = run_scraper_script(user_creds[0]["UserInfo"]["DOP_ID"], decrypted_password, lists_json),

                                if result.stdout:
                                    st.success(f"List '{lst['listName']}' processed successfully!")
                                    with st.expander("Script Output"):
                                        st.code(result.stdout)
                                
                                if result.stderr:
                                    st.error("Errors occurred:")
                                    st.code(result.stderr)
                            else:
                                st.error("User credentials not found")
                        except Exception as e:
                            st.error(f"Error generating list: {e}")

                    # Purge list button (keep this from original code)
                    if action_cols[2].button("🗑 Purge List", key=f"purge_{lst['_id']}", type="primary"):
                        purge_list(lst["_id"])  

def main():

    load_session()
    
    if not st.session_state.get("logged_in", False):
        login_page()
        return 

    st.sidebar.title("Navigation")

    # with st.sidebar.container():
    #     st.markdown("### Navigation Options")
    #     # st.divider()
    #     page = st.selectbox("📌 Go to", ["Account View", "List View", "Change Password", "Add New Account", "Delete Account", "Logout"], key="user_settings")

    page = st.sidebar.selectbox("Select", ["Account View","List View", "Change Password","Add New Account","Delete Account" ,"Logout"], key="user_settings")

    if page == "Change Password":
        settings.show_password_change_form(fernet,get_user_creds(),db.user_collection)
        return  
    elif page == "Add New Account":
        settings.show_add_new_account_form(collection)
        return
    elif page == "Delete Account":
        settings.show_delete_account_form(collection)
        return
    
    elif page == "Logout":

        clear_session()

        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun() 

    if page == "Account View":
        account_view()
    elif page == "List View":
        list_view()

if __name__ == "__main__":
    main()