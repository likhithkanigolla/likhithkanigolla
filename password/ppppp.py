from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def check_pass(pw, email, username):
    if len(pw) < 8 or not (any(c.isupper() for c in pw) and any(c.islower() for c in pw) and any(c.isdigit() for c in pw)):
        return False
    if pw.lower() == email.lower() or pw.lower() == username.lower():
        return False
    if not username:
        username = email
    # Additional checks can be added here
    return True

@app.route('/', methods=['GET', 'POST'])
def index():
    result_message = None

    if request.method == 'POST':
        try:
            pw = request.form.get('password')
            email = request.form.get('email')
            username = request.form.get('username')

            is_password_strong = check_pass(pw, email, username)

            if is_password_strong:
                return redirect(url_for('result', result='Password is strong!'))
            else:
                result_message = 'Password is not strong.'

        except Exception as e:
            result_message = f"An error occurred: {str(e)}"

    return render_template('index.html', result=result_message)

@app.route('/result')
def result():
    result_message = request.args.get('result', 'No result available.')
    return render_template('result.html', result=result_message)

if __name__ == '__main__':
    app.run(debug=True)
