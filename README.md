# API Server for IOT Project - Smart Door unlocked by speech
This is the server for IOT Project - Smart Door unlocked by speech of team 9.

## Our team
| Name              | Student ID | Mail                           |
|-------------------|------------|--------------------------------|
| Do Duc Manh       | 20210567   | manh.dd210567@sis.hust.edu.vn  |
| Cao Minh Tue      | 20210908   | tue.cm210908@sis.hust.edu.vn   | 
| Nghiem Minh Hieu  | 20210333   | hieu.nm210333@sis.hust.edu.vn  |
| Nguyen Dang Duong | 20215336   | duong.nd215336@sis.hust.edu.vn |  


## Folder structure
```
.
├── main.py                 # main core of server
├── model                   # contains audio model we use
│   └── ...
├── config                  # conainns config of server (create your own .env here)
|   └── .env
├── apps                    # contains various components of server
│   ├── routers.py
|   ├── models.py
|   └── voice.py
├── test                    # test scripts
│   └── ...
```

## Deploy
This server got delpoyed on Render: https://iot-server-luym.onrender.com

**Note:** Because of limit of the Render free tier, the server may not work.

## Local
If you want to run this project locally.

**Step 1:** Create venv and install requirements

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**Step2:** Create .env file
```
APP_NAME=[INSERT HERE]
DEBUG_MODE=[INSERT HERE]

HOST=[INSERT HERE]
PORT=[INSERT HERE]

DB_URL=[INSERT HERE]
DB_NAME=[INSERT HERE]
```

**Step3:** Start server
```
python main.py
```
