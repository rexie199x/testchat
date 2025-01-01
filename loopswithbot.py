import streamlit as st
import pandas as pd
import psycopg2
import os

# Database connection
def get_db_connection():
    try:
        return psycopg2.connect(
            host=os.getenv("host"),
            database=os.getenv("database"),
            user=os.getenv("user"),
            password=os.getenv("password"),
        )
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        return None

# Function to load processes data from the database
def load_processes_data():
    conn = get_db_connection()
    if not conn:
        return {}

    cur = conn.cursor()
    try:
        cur.execute("SELECT section, title, content FROM public.ops_processes")
        rows = cur.fetchall()
    except Exception as e:
        st.error(f"Error executing SQL query: {e}")
        rows = []
    finally:
        cur.close()
        conn.close()

    data = {}
    for row in rows:
        section, title, content = row
        if section not in data:
            data[section] = []
        data[section].insert(0, {"title": title, "content": content})  # Insert at the beginning
    return data

# Chatbot function to query the database based on user input
def chatbot_query(user_input):
    conn = get_db_connection()
    if not conn:
        return "Sorry, I couldn't connect to the database."

    cur = conn.cursor()
    try:
        # Check if user query matches any process title or content
        cur.execute("""
            SELECT title, content FROM public.ops_processes
            WHERE title ILIKE %s OR content ILIKE %s
            LIMIT 1
        """, ('%' + user_input + '%', '%' + user_input + '%'))
        result = cur.fetchone()

        if result:
            return f"Title: {result[0]}\nContent: {result[1]}"
        else:
            return "Sorry, I couldn't find any relevant information."
    except Exception as e:
        st.error(f"Error executing SQL query: {e}")
        return "Sorry, I encountered an error while processing your request."
    finally:
        cur.close()
        conn.close()

# Initialize chatbot UI
def show_chatbot():
    st.title("Chatbot - Ask me anything!")

    user_input = st.text_input("Ask a question:")

    if st.button("Ask"):
        if user_input:
            response = chatbot_query(user_input)
            st.write("Bot's response:")
            st.text_area("", response, height=200, max_chars=None, key="response_area", disabled=True)
        else:
            st.warning("Please enter a question.")

# Main function to run the app
def main():
    st.sidebar.image("https://lonelyoctopus.s3.eu-north-1.amazonaws.com/LOOPS.png", width=280)
    st.sidebar.title("Menu")
    
    # Inject custom CSS
    st.markdown(
        """
        <style>
        .stButton>button:hover {
            background-color: purple !important;
            color: white !important;
        }
        .stButton>button {
            width: 100%;
        }
        .full-screen-iframe {
            position: fixed;
            top: 5;
            left: 330px;
            width: calc(100% - 350px);
            height: calc(90% - 20px);
            border: none;
            z-index: 9999;
        }
        .custom-padding {
            padding: 5px !important;
        }
        .css-1d391kg {
            width: 330px !important;
            position: fixed !important;
            top: 0;
            left: 0;
            height: 100vh;
        }
        .css-18ni7ap {
            margin-left: 330px !important;
        }
        .css-15tx938, .css-1rs6os.edgvbvh10 {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    menu_options = ["General Processes", "Discord Related Processes", "Email Templates", "Document Templates", "Templates", "Links", "Timelines", "Dashboard", "Chatbot"]
    choice = st.sidebar.radio("Go to", menu_options, index=0)  # Default to "Dashboard" page

    if choice == "Dashboard":
        st.markdown("<div class='custom-padding'></div>", unsafe_allow_html=True)
        # Embed Looker Studio report
        st.write(
            """
            <iframe class="full-screen-iframe" src="https://lookerstudio.google.com/embed/reporting/d3b5906b-d484-41c6-b925-b0105be21448/page/rHc7D" frameborder="0" style="border:0" allowfullscreen></iframe>
            """,
            unsafe_allow_html=True
        )
    elif choice == "Checklist":
        show_checklist()
    elif choice == "Chatbot":
        show_chatbot()
    else:
        show_processes(choice)

if __name__ == "__main__":
    main()
