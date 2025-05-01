#=================flask code starts here
from flask import Flask, render_template, request, redirect, url_for, session,send_from_directory
import os
from werkzeug.utils import secure_filename
from distutils.log import debug
from fileinput import filename
from werkzeug.utils import secure_filename
import sqlite3
import pickle
import random

import smtplib 
from email.message import EmailMessage
from datetime import datetime

import pandas as pd
import numpy as np
from sklearn.metrics import max_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt #use to visualize dataset values
import seaborn as sns
from sklearn.metrics import mean_squared_error
from math import sqrt
from keras.models import Sequential, load_model
import os
import pickle


UPLOAD_FOLDER = os.path.join('static', 'uploads')
# Define allowed files
#loading and displaying Aneshtesia clinical dataset
dataset = pd.read_csv("Dataset/Pan_10degC.csv", usecols=['Voltage','Current','Temperature','Capacity','Voltage_Average','Current_Average'])
#handling and removing missing values        
dataset.fillna(0, inplace = True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'welcome'


#class to normalize dataset values
scaler = MinMaxScaler(feature_range = (0, 1))
scaler1 = MinMaxScaler(feature_range = (0, 1))

Y = dataset.values[:,3:4]
dataset.drop(['Capacity'], axis = 1,inplace=True)
X = dataset.values
X = scaler.fit_transform(X)
Y = scaler1.fit_transform(Y)

X = np.reshape(X, (X.shape[0], X.shape[1], 1))
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)



@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/notebook')
def notebook():
    return render_template('SOCEstimation.html')


@app.route('/PredictAction', methods=['GET', 'POST'])
def PredictAction():

    if request.method == 'POST':
        data = request.form['t1']
        arr = data.split(",")
        test = []
        for i in range(len(arr)):
            test.append(float(arr[i].strip()))
        test = np.asarray(test)
        temp = []
        temp.append(test)
        test = np.asarray(temp)
        testData = scaler.transform(test)#normalize test data
        testData = np.reshape(testData, (testData.shape[0], testData.shape[1], 1, 1))
        cnn_model = load_model("model/cnn_weights.hdf5")
        predict_soc = cnn_model.predict(testData)#apply CNN model to predict State of Charge
        predict_soc = predict_soc.reshape(-1, 1)
        predict_soc = scaler1.inverse_transform(predict_soc)#reverse normalize predicted SOC to normal integer value
        output = "Test Data = "+str(data)+" Predicted State Of Charge (SOC) ====> "+str(abs(predict_soc[0]))
        return render_template('result.html', msg=output)

@app.route('/logon')
def logon():
	return render_template('signup.html')

@app.route('/login')
def login():
	return render_template('signin.html')

@app.route("/signup")
def signup():
    global otp, username, name, email, number, password
    username = request.args.get('user','')
    name = request.args.get('name','')
    email = request.args.get('email','')
    number = request.args.get('mobile','')
    password = request.args.get('password','')
    otp = random.randint(1000,5000)
    print(otp)
    msg = EmailMessage()
    msg.set_content("Your OTP is : "+str(otp))
    msg['Subject'] = 'OTP'
    msg['From'] = "myprojectstp@gmail.com"
    msg['To'] = email
    
    
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("myprojectstp@gmail.com", "paxgxdrhifmqcrzn")
    s.send_message(msg)
    s.quit()
    return render_template("val.html")

@app.route('/predict_lo', methods=['POST'])
def predict_lo():
    global otp, username, name, email, number, password
    if request.method == 'POST':
        message = request.form['message']
        print(message)
        if int(message) == otp:
            print("TRUE")
            con = sqlite3.connect('signup.db')
            cur = con.cursor()
            cur.execute("insert into `info` (`user`,`email`, `password`,`mobile`,`name`) VALUES (?, ?, ?, ?, ?)",(username,email,password,number,name))
            con.commit()
            con.close()
            return render_template("signin.html")
    return render_template("signup.html")

@app.route("/signin")
def signin():

    mail1 = request.args.get('user','')
    password1 = request.args.get('password','')
    con = sqlite3.connect('signup.db')
    cur = con.cursor()
    cur.execute("select `user`, `password` from info where `user` = ? AND `password` = ?",(mail1,password1,))
    data = cur.fetchone()

    if data == None:
        return render_template("signin.html")    

    elif mail1 == str(data[0]) and password1 == str(data[1]):
        return render_template("home.html")
    else:
        return render_template("signin.html")


    
if __name__ == '__main__':
    app.run()