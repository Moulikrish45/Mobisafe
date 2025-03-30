🚗 AutoIntell Backend - Predictive Vehicle Health Monitoring
🚀 A Django-based API for real-time vehicle monitoring & predictive maintenance using Machine Learning models!


📌 Features
✅ 🔐 Secure JWT Authentication - Login & protect API access
✅ 🚘 Real-time Sensor Data API - Fetch latest vehicle readings
✅ 📊 Predictive Analytics - ML models detect engine health issues
✅ 🛢️ PostgreSQL Database - Securely stores user & sensor data


🚀 Tech Stack
Technology	                                Usage
🐍 Django + DRF	                            Backend & API Development
🗄️ PostgreSQL	                              Database for storing sensor data & users
🔑 JWT (JSON Web Token)	                    Secure authentication
🤖 TensorFlow & XGBoost	                    Machine Learning for engine health
📡 Flutter Secure Storage	                  Stores tokens for mobile authentication  (FRONTENDSIDE LOCAL STORAGE)


📂 Project Structure

AutoIntel_Backend/
│── autointel/               # 🌍 Main Django project
│   │── settings.py          # ⚙️ Project settings (PostgreSQL config)
│   │── urls.py              # 🌐 Global URL routing
│
│── authentication/          # 🔐 User authentication
│   │── views.py             # 🔑 Login & JWT authentication
│   │── urls.py              # 🌐 Auth API routing
│
│── sensor_api/              # 🚘 Vehicle sensor data API
│   │── models.py            # 🗄️ PostgreSQL models
│   │── views.py             # 🛠️ API logic
│   │── urls.py              # 🔗 API routes
│   │── serializers.py       # 🔄 Data serialization
│
│── ml_models/               # 🤖 Machine Learning models
│   │── engine_health/       # 🛠️ Engine health prediction
│   │   │── train.py         # 🏋️‍♂️ Training script
│   │   │── predict.py       # 🔮 Prediction script
│   │   │── model_lstm.py    # 🧠 LSTM model
│   │   │── preprocessing.py # 🔄 Data preprocessing
│   │   │── datasets/        # 📊 Training datasets
│   │   │── model_weights/   # 💾 Trained models
│
│── manage.py                # 🚀 Django project manager
│── requirements.txt         # 📜 Dependencies
│── README.md                # 📖 Documentation
│── .env                     # 🔑 Database credentials


🎯 Installation & Setup
1️⃣ Install Dependencies

Ensure Python 3.9+ is installed, then run:

pip install -r requirements.txt

2️⃣ Setup PostgreSQL Database

Create a .env file and configure:

DB_NAME=autointell_db
DB_USER=autointell_user
DB_PASSWORD=autointell_password
DB_HOST=localhost
DB_PORT=5432

Apply migrations:

python manage.py makemigrations
python manage.py migrate

3️⃣ Run the Server 
python manage.py runserver

The API will be live at: http://127.0.0.1:8000/

 

🔗 API Endpoints

🔑 Authentication API
Method	        Endpoint	                    Description
POST	          /api/auth/register/           Register a new user
POST	          /api/auth/login/	            Login & receive JWT token
POST	          /api/auth/logout/	            Logout user & invalidate token

🚗 Vehicle Sensor API
Method	        Endpoint	                                Description
GET	            /api/sensor/latest/{vehicle_id}/	        Get latest sensor readings
POST	          /api/sensor/add/	                        Add new sensor data

🤖 Machine Learning API
Method	        Endpoint	                    Description
POST	          /api/ml/predict/engine/	      Predict engine health using LSTM model


🎯 Testing the API

Use Postman or cURL to test.
🔹 Example: Login User

curl -X POST http://127.0.0.1:8000/api/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "password123"}'

✅ Expected Response

{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5..."
}

🔹 Example: Predict Engine Health

curl -X POST http://127.0.0.1:8000/api/ml/predict/engine/ \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -d '{
        "engine_rpm": 1500,
        "lub_oil_pressure": 30.5,
        "fuel_pressure": 40.2,
        "coolant_pressure": 18.7,
        "lub_oil_temp": 75.3,
        "coolant_temp": 85.0
    }'

✅ Expected Response

{
    "lstm_prediction": 0.92,
    "engine_condition": 1
}

🚀 Next Steps

✅ Backend is ready!
   Android application frontend @ https://github.com/BudraHH/AutoIntell_AUI (Vehicle dashboard application)


👨‍💻 Contributor: Hari Hara Budra - Lead Developer 🚀


📝 License
📜 This project is open-source under the MIT License.
