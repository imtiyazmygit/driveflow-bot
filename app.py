from flask import Flask, render_template, request, redirect, url_for
import os


def create_app():
    app = Flask(__name__)

    @app.route('/', methods=['GET', 'POST'])
    def index():
        status = None
        if request.method == 'POST':
            centre = request.form.get('centre', '').strip()
            if centre:
                status = f"Booking request received for {centre}. The automation will run from the server side."
            else:
                status = 'Please choose a test centre.'
        return render_template('index.html', status=status)

    return app


app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)
