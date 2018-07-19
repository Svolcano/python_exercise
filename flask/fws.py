from flask import Flask
from flask import render_template
from flask import url_for
from flask import Markup
from flask import redirect
from flask import request
from flask import abort
from flask import flash
from bky import get_log
import os

app = Flask(__name__)


@app.route("/news/<int:n>")
def hello(n):
    all_list = get_log(1, n)
    return render_template('index.html', all_list=all_list)


def get_img_path():
    home = f"{app.static_folder}/image"
    print("***", home)
    all_path = []
    for root, dirs, files in os.walk(home):
        print(root, dirs, files)
        for f in files:
            all_path.append(f)
    print(all_path)
    return all_path


@app.route('/img/')
def tell_me_path():
    print('hel')
    img_paths = get_img_path()
    return render_template('img.html', img_paths=img_paths)


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
    app.run(debug=True, host='0.0.0.0', port=8090)
    
    
