import os
from flask import Flask, redirect, request, session, url_for
from flask_session import Session
import msal

app = Flask(__name__)
app.secret_key = "test-secret"  # replace with something secure
app.config["SESSION_TYPE"] = "null"  # use signed cookies only
Session(app)

# 🔹 Put your Entra ID settings here (use Azure App Service → Configuration in production)
CLIENT_ID = os.getenv("CLIENT_ID", "your-client-id-here")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "your-client-secret-here")
AUTHORITY = os.getenv("AUTHORITY", "https://login.microsoftonline.com/your-tenant-id")
REDIRECT_URI = os.getenv("REDIRECT_URI", "https://synesthetica.azurewebsites.net/getAToken")
SCOPE = ["User.Read"]

@app.route("/")
def home():
    if not session.get("user"):
        return '<a href="/login">🔐 Login with Microsoft Entra ID</a>'
    return f"✅ Logged in as {session['user']['name']} <br><a href='/logout'>Logout</a>"

@app.route("/login")
def login():
    # create auth flow
    flow = _build_msal_app().initiate_auth_code_flow(scopes=SCOPE, redirect_uri=REDIRECT_URI)
    session["flow"] = flow
    return redirect(flow["auth_uri"])

@app.route("/getAToken")
def authorized():
    try:
        result = _build_msal_app().acquire_token_by_authorization_code(
            request.args["code"],
            scopes=SCOPE,
            redirect_uri=REDIRECT_URI
        )
        if "error" in result:
            return f"Login error: {result['error_description']}"
        session["user"] = result.get("id_token_claims")
    except Exception as e:
        return str(e)
    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        f"{AUTHORITY}/oauth2/v2.0/logout?post_logout_redirect_uri={url_for('home', _external=True)}"
    )

def _build_msal_app():
    return msal.ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
