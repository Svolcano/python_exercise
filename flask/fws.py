from flask import Flask
from flask import render_template
from flask import url_for
from flask import Markup
from flask import redirect
from flask import request
from flask import abort
from flask import flash

app = Flask(__name__)


@app.route("/")
def hello():
    return Markup('<strong>Hello %s!</strong>') % '<blink>hacker</blink>'


@app.route('/hello')
@app.route('/hello/<name>')
def tell_me_path(name=None):
    return render_template('hello.html', name=name)

@app.route('/u/<username>')
def get_user_name(username):
    print(request.headers)
    print(dir(request))
    return redirect(url_for('hello'))


@app.route('/post/<int:id>')
def get_post_id(id):
    flash('e4rrorr 404')
    abort(401)
    return str(id)


if __name__ == "__main__":
    app.secret_key = 'OTFQfbKrleM='
    app.run(debug=True, port=80)
