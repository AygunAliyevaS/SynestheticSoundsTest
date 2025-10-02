import os
from flask import Flask, redirect, request
import msal

app = Flask(__name__)

# 🔹 Environment variables (set these in Azure App Service → Configuration → Application settings)
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
AUTHORITY = os.getenv("AUTHORITY")  # e.g. https://login.microsoftonline.com/<tenant-id>
REDIRECT_URI = os.getenv("REDIRECT_URI")  # e.g. https://synesthetica.azurewebsites.net/getAToken
SCOPE = ["User.Read"]

@app.route("/")
def home():
    return '<a href="/login">🔐 Login with Microsoft Entra</a>'

@app.route("/login")
def login():
    msal_app = msal.ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
    )
    flow = msal_app.initiate_auth_code_flow(SCOPE, redirect_uri=REDIRECT_URI)
    # store the flow in memory (not session, just quick test)
    app.flow = flow
    return redirect(flow["auth_uri"])

@app.route("/getAToken")
def authorized():
    try:
        msal_app = msal.ConfidentialClientApplication(
            CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
        )
        result = msal_app.acquire_token_by_authorization_code(
            request.args["code"],
            scopes=SCOPE,
            redirect_uri=REDIRECT_URI
        )
        return result  # just dump JSON response to test
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
