import json
import boto3
from io import StringIO

s3 = boto3.resource('s3')

def lambda_handler(event, context):
    
    #get sensor reading from s3 bucket
    s3_object = s3.Bucket('tempsensorbucket').Object('temperaturereading').get()
    sensor_reading = s3_object['Body'].read()
    
    #yes it has to be done in 3 lines, otherwise it will cry about not being able to slice int...
    sensor_reading_string = sensor_reading.decode('utf-8')#decode from byte to string
    sensor_reading_string = sensor_reading_string.replace("\"", "")#remove trash from the data
    sensor_reading_string = sensor_reading_string.replace("[", "")
    sensor_reading_string = sensor_reading_string.replace("]", "")
    sensor_reading_list = sensor_reading_string.split(" ")#split into 3 parts
    
    #paste sensor reading to wrap html code around it and then send it to the screen
    return display_page(sensor_reading_list)
    
def display_page (sensor_reading):
    #wrap the reading in the html code
    content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <title>Temperature sensor</title>
    
    <link rel="stylesheet" href="https://use.typekit.net/oov2wcw.css">
    <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    
    <style>
    body,h1,h2,h4 {font-family: century-gothic, sans-serif}
    </style>
    </head>
    
    <body>
    <header class="w3-container w3-blue w3-center" style="padding:128px 16px">
    
    <h1 class="w3-margin w3-jumbo">""" + "Sensor reads - " + sensor_reading[0] + """ Degree Celcius</h1>
    <h2>The temperature reading was taken at """ + sensor_reading[1] + " " + sensor_reading[2] + """</h2>
    
    <button onClick="refresh(this)" class="w3-button w3-black w3-padding-large w3-large w3-margin-top">Refresh</button>
    </header>
    
    <div class="w3-container" style="padding:16px 16px; text-align:center">
      <h1>CMP408 mini project</h1>
      <h4>For my CMP408 mini project, I have created a temperature sensor controlled by Raspberry pi with an HTML interface. The Raspberry pi takes a temperature reading using the DHL11 sensor. Then that reading is displayed here.</h4>
    </div>
    </body>
    
    <script>
    function refresh(){
        window.location.reload("Refresh")
      }
    </script>
    </html>
    """
    
    response = {
    'statusCode': 200,
    'body': content,
    'headers': {'Content-Type': 'text/html',},
               }
    return response