import streamlit as st
import requests

# Facebook Graph API URL
FB_GRAPH_API = "https://graph.facebook.com/v17.0"

# Load fanpage access tokens from Streamlit secrets
page_access_tokens = st.secrets["facebook"]["page_access_tokens"]

# Streamlit App
st.title("Facebook Post Sharer")
st.markdown("Share a post to multiple Facebook fan pages with one click.")

# Input fields
post_message = st.text_area("Post Message", "Write your Facebook post here...")
image_url = st.text_input("Image URL (optional)", "")
submit_button = st.button("Share Post")

if submit_button:
    if not post_message:
        st.error("Post message cannot be empty!")
    elif not page_access_tokens:
        st.error("No fan pages found! Please add your tokens in Streamlit Cloud Secrets.")
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
    1. Go to Streamlit Cloud → App Settings → Secrets.
    2. Add the following to your secrets:
       ```toml
       [facebook]
       page_access_tokens = [
           "page_access_token_1",
           "page_access_token_2",
           "... up to 25 tokens ..."
       ]
       ```
    3. Redeploy your app to apply the changes.
    """)
