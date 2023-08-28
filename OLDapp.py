# app.py



# from flask import Flask, render_template, request
# app = Flask(__name__)

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     # Logic for getting data and plotting will go here
#     return render_template('index.html')  # This will render an HTML template


# if __name__ == '__main__':
#     app.run(debug=True)



from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    plot_url = None
    if request.method == 'POST':
        selected_date = request.form['selected_date']
        
        # Your code for loading the dataset and generating the chart based on the selected_date goes here
        
        # Convert plot to PNG image
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode('utf8')

    return render_template('index.html', plot_url=plot_url)

    
if __name__ == '__main__':
    app.run(debug=True)
