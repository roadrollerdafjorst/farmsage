from flask import Flask, render_template, request, url_for
from WeartherForecastModule import WeatherForecast
from NutrientsPredictorModule import nutrients_predictor

# Initialize Flask application
app = Flask(__name__)

# Define a route for the default URL, which loads the form
@app.route('/processing/', methods=['GET', 'POST'])
def processing():
    if request.method == "GET":
        print("The URL /processing is accessed directly.")
        return url_for('index.html')

    # POST request
    if request.method == "POST":
        form_data = request.form
        call_success = []
        npk_list_dict = []
        popup_data = []
        seven_days = []

        # get the form data
        crop = form_data['crop']
        state = form_data['state']
        city = form_data['city']

        # write the form data to a csv file
        with open("InputData.csv", "w") as f:
            input_data = "%s,%s,%s" % (crop.strip(), state.strip(), city.strip())
            f.write(input_data)
        
        # call the weather forecast module
        forecaster = WeatherForecast(city_name = city, state_name = state)
        forecaster.api_caller()

        # check if the api call was successful
        if forecaster.is_api_call_success():
            category, heading, desc = forecaster.get_weather_data()

            call_success.append(1)
            popup_data.append([category, heading, desc])
            seven_days = forecaster.weather_data[:]\
                
            # get the weather data
            di = forecaster.weather_data[0]
            temp = di['Temperature']
            humidity = di['Relative Humidity']
            rainfall = di["Rainfall"]

            # get the nutrients prediction
            npk = {'Label_N': 0, 'Label_P': 0, 'Label_K': 0}
            for y_label in ['Label_N', 'Label_P', 'Label_K']:
                npk[y_label] = nutrients_predictor(crop, temp, humidity, rainfall, y_label)

            npk_list_dict.append(npk)

            # write the output data to a file
            output_data = category +"\n"+ heading +"\n"+ desc +"\n"+ str(npk['Label_N'])  +"\n"+ str(npk['Label_P'])  +"\n"+ str(npk['Label_K'])
            with open("output.txt", "w") as fh:
                fh.write(output_data)
        else:
            print("Error Occured")
            
        return render_template('update.html', CALL_SUCCESS = call_success, NPK = npk_list_dict, FORM_DATA = form_data, POPUP_DATA = popup_data, SEVEN_DAYS = seven_days)
    
# Define a route for the default URL
@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)