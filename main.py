import streamlit as st
import requests
import json

# Facebook Graph API URL
FB_GRAPH_API = "https://graph.facebook.com/v17.0"

# Load fanpage access tokens from the JSON file
def load_fanpages():
    try:
        with open("fanpages.json", "r") as f:
            data = json.load(f)
            return data["fanpages"]
    except Exception as e:
        st.error(f"Error loading fanpages.json: {e}")
        return []

# Streamlit App
st.title("Facebook Post Sharer")
st.markdown("Share a post to multiple Facebook fan pages with one click.")

# Input fields
post_message = st.text_area("Post Message", "Write your Facebook post here...")
image_url = st.text_input("Image URL (optional)", "")
submit_button = st.button("Share Post")

# Load fanpages
page_access_tokens = load_fanpages()

if submit_button:
    if not post_message:
        st.error("Post message cannot be empty!")
    elif not page_access_tokens:
        st.error("No fan pages found! Please check fanpages.json.")
    else:
        # Function to post to a Facebook page
        def post_to_page(page_id, access_token, message, image_url=""):
            url = f"{FB_GRAPH_API}/{page_id}/feed"
            payload = {
                "message": message,
                "access_token": access_token
            }
            if image_url:
                payload["link"] = image_url

            response = requests.post(url, data=payload)
            return response.json()

        # Iterate over pages and share the post
        results = []
        for token in page_access_tokens:
            # Get page ID from access token
            page_id = requests.get(
                f"{FB_GRAPH_API}/me",
                params={"access_token": token}
            ).json().get("id")

            if page_id:
                result = post_to_page(page_id, token, post_message, image_url)
                results.append((page_id, result))
            else:
                results.append(("Unknown", {"error": "Invalid access token"}))

        # Display results
        for page_id, result in results:
            if "error" in result:
                st.error(f"Error posting to Page {page_id}: {result['error']['message']}")
            else:
                st.success(f"Post successfully shared on Page {page_id}!")

# Instructions to set up environment
if st.checkbox("Show Setup Instructions"):
    st.markdown("""
    ### Setup Instructions
    1. Create a file called `fanpages.json` in your project directory.
    2. Add your page access tokens in the following format:
       ```json
       {
           "fanpages": [
               "page_access_token_1",
               "page_access_token_2",
               "... up to 25 tokens ..."
           ]
       }
       ```
    3. Deploy your app, and ensure the `fanpages.json` file is included in your project.
    """)
