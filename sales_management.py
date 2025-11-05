import streamlit as st
import pandas as pd
import csv, os, random
from io import StringIO

# --- FILE PATHS (Streamlit equivalent: st.session_state for persistence) ---
SALES_FILE = "sales_data.csv"
CUSTOMERS_FILE = "customers.csv"
PRODUCTS_FILE = "products.csv"

# --- Streamlit Setup ---
st.set_page_config(layout="wide", page_title="AI Sales Bot 🤖 (CFA)")
st.title("AI Sales Management Bot (CFA)")

# --- Initialization of Session State ---
if 'messages' not in st.session_state:
    st.session_state['messages'] = [{"role": "bot", "content": "Hello! I'm your AI Sales Manager 🤖\nTry 'add sale apple 5 200' to begin."}]
if 'sales_df' not in st.session_state:
    st.session_state['sales_df'] = pd.DataFrame(columns=["Product", "Quantity", "Price (CFA)", "Total (CFA)"])
if 'customers_df' not in st.session_state:
    st.session_state['customers_df'] = pd.DataFrame(columns=["Customer Name"])
if 'products_df' not in st.session_state:
    st.session_state['products_df'] = pd.DataFrame(columns=["Product", "Price (CFA)"])

# ----------------------------------------------------
# --------- DATA MANAGEMENT (Using Pandas/CSV) ---------
# ----------------------------------------------------

# Note: In a deployed Streamlit app, writing to CSV files directly is ephemeral.
# For permanent storage, you'd use a cloud database (like Streamlit connection to SQLite/Postgres).
# For this conversion, we'll use Streamlit's cache and session state for data persistence
# during a single user session and mimic file loading/saving.

@st.cache_data(show_spinner=False)
def load_data(file_path, columns):
    """Loads data from CSV or initializes a DataFrame."""
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path, header=None, names=columns)
            return df
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

def save_data(df, file_path):
    """Saves DataFrame to CSV file."""
    df.to_csv(file_path, index=False, header=False)

def refresh_all_data():
    """Loads all data and updates session state DFs."""
    with st.spinner("Loading Data..."):
        # SALES
        sales_cols = ["Product", "Quantity", "Price (CFA)", "Total (CFA)"]
        st.session_state['sales_df'] = load_data(SALES_FILE, sales_cols)
        
        # CUSTOMERS
        customer_cols = ["Customer Name"]
        st.session_state['customers_df'] = load_data(CUSTOMERS_FILE, customer_cols)
        
        # PRODUCTS
        product_cols = ["Product", "Price (CFA)"]
        st.session_state['products_df'] = load_data(PRODUCTS_FILE, product_cols)

def calculate_total():
    """Calculates total sales from the current sales DataFrame."""
    if not st.session_state['sales_df'].empty:
        return st.session_state['sales_df']["Total (CFA)"].sum()
    return 0

# --- Initial Data Load ---
refresh_all_data()

# ----------------------------------------------------
# --------- CHATBOT LOGIC (Streamlit-fied) ---------
# ----------------------------------------------------

def bot_reply(msg):
    """Processes user message and returns a bot response."""
    msg = msg.lower().strip()
    response = ""

    if "hello" in msg or "hi" in msg:
        response = random.choice(["Hey there! 😊", "Hello boss! Ready to record some sales?", "Hi! What are we selling today?"])
    
    elif "add sale" in msg:
        try:
            parts = msg.split()
            # e.g. "add sale apple 5 200"
            product = parts[2]
            quantity = int(parts[3])
            price = float(parts[4])
            total = quantity * price
            
            # Append to DataFrame
            new_sale = pd.DataFrame([{"Product": product, "Quantity": quantity, "Price (CFA)": price, "Total (CFA)": total}])
            st.session_state['sales_df'] = pd.concat([st.session_state['sales_df'], new_sale], ignore_index=True)
            save_data(st.session_state['sales_df'], SALES_FILE)
            
            response = f"✅ Added {quantity} {product}(s) at {price:.2f} CFA each."
        except Exception:
            response = "⚠️ Please say: add sale [product] [quantity] [price]"
    
    elif "total" in msg:
        total = calculate_total()
        response = f"💰 Total sales so far: **{total:,.2f} CFA**"
    
    elif "show sales" in msg or "view sales" in msg:
        # Data is already shown in the table, just confirm refresh
        refresh_all_data() # Ensure the table widget updates
        response = "📊 Sales list refreshed!"
    
    elif "add customer" in msg:
        try:
            name = msg.replace("add customer", "").strip().capitalize()
            if name:
                # Append to DataFrame
                new_customer = pd.DataFrame([{"Customer Name": name}])
                st.session_state['customers_df'] = pd.concat([st.session_state['customers_df'], new_customer], ignore_index=True)
                save_data(st.session_state['customers_df'], CUSTOMERS_FILE)
                refresh_all_data()
                response = f"👤 Customer '{name}' added successfully."
            else:
                response = "⚠️ Please provide a customer name."
        except:
            response = "❌ Error adding customer."
    
    elif "add product" in msg:
        try:
            # e.g. "add product rice 400"
            parts = msg.split()
            name = parts[2]
            price = float(parts[3])
            
            # Append to DataFrame
            new_product = pd.DataFrame([{"Product": name, "Price (CFA)": price}])
            st.session_state['products_df'] = pd.concat([st.session_state['products_df'], new_product], ignore_index=True)
            save_data(st.session_state['products_df'], PRODUCTS_FILE)
            refresh_all_data()
            response = f"📦 Product '{name}' added at {price:.2f} CFA."
        except Exception:
            response = "⚠️ Please say: add product [name] [price]"
    
    elif "thank" in msg:
        response = "You're welcome! 😄"
    
    elif "clear" in msg:
        # Clear chat history in session state
        st.session_state['messages'] = [{"role": "bot", "content": "Chat cleared 🧹"}]
        # Rerun the app to update the chat
        st.rerun() 
        return "Chat cleared 🧹" # This response won't be shown, as the app reruns
        
    elif "bye" in msg:
        response = "Goodbye 👋"
        
    else:
        response = random.choice([
            "I'm not sure I understand 🤔. Try 'add sale apple 5 200'",
            "I can help with sales, products, and customers 💼",
            "Try 'show sales' or 'total' to begin!"
        ])
        
    return response

# ----------------------------------------------------
# --------- STREAMLIT UI LAYOUT ---------
# ----------------------------------------------------

col1, col2 = st.columns([1, 2])

with col1:
    st.header("💬 Sales Chatbot")
    
    # Display the chat history
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        # Use st.chat_message for a native chat UI
        with st.chat_message(role):
            st.markdown(content)
            
    # Chat input box
    if prompt := st.chat_input("Enter command (e.g., add sale apple 5 200)"):
        # 1. Add user message to state
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 2. Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # 3. Get bot response
        response = bot_reply(prompt)
        
        # 4. Add bot response to state and display
        with st.chat_message("bot"):
            st.markdown(response)
        
        st.session_state.messages.append({"role": "bot", "content": response})


with col2:
    st.header("📊 Sales & Records")
    
    # --- Sales Table ---
    st.subheader("Sales Records")
    st.dataframe(st.session_state['sales_df'], use_container_width=True, hide_index=True)
    
    st.info(f"💰 **Total Sales**: **{calculate_total():,.2f} CFA**")
    
    # --- Other Tables using tabs for better layout ---
    tab1, tab2 = st.tabs(["👥 Customers", "📦 Products"])
    
    with tab1:
        st.dataframe(st.session_state['customers_df'], use_container_width=True, hide_index=True)

    with tab2:
        st.dataframe(st.session_state['products_df'], use_container_width=True, hide_index=True)

# Note: The original Tkinter app's `root.mainloop()` is replaced by Streamlit's implicit loop.