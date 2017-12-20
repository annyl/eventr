from flask import Flask, request, render_template
from search_news import Eventr
app = Flask(__name__)


@app.route('/', methods=["GET", "POST"])
def search():
    return render_template('search.html')


@app.route('/search', methods=["GET", "POST"])
def get_news():
    eventr = Eventr(request.args['city']) if request.args['city'] else Eventr()
    events = eventr.get_news(request.args.get('q'))
    return render_template('list.html', events=events, query=request.args['q'])


if __name__ == '__main__':
    app.run(host='localhost', port=8081, debug=True)
