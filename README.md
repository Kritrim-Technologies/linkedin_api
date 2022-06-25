# Linkedin_API

[`libkedin_API`](https://github.com/bi-kash/linkedin_api) is an linkedin scrapper for getting information out of linkedin using its voager api. If you would like assistance with using the tradelib you can email us at bikashtimsina76@gmail.com.

# Installation instruction
1. Assumption is you already have python3 installed on your machine
2. Build and enter into virtual environment

    ```
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3. Install necessary modules
    ```
    pip3 install -r requirements.txt
    ```

# API documentation
1. Login to api. It's a simple authentication system. No user registration of any kind and no database.
    Note: Password=thisisthesecretkey
    ```
    curl -u username 127.0.0.1:5000/login_api

    ```
    It asks for the password. After entering a password it gives a token that lasts for 60 minutes. Please copy that somewhere
    

2. Provide linkedin credential
    ```
    curl -XGET -G 127.0.0.1:5000/api/login_linkedin --data-urlencode 'username=youremail@gmail.com' --data-urlencode 'password=yourpassword'
    ```

3. Get information about your own profile
    ```
    curl -XGET http://127.0.0.1:5000/api/me?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiYmlrYXNoIiwiZXhwIjoxNjU2MTU0MDY5fQ.3wmgfQfPNYUpdUh954rULKdKYgBzL8N0UAPnSu7Qxt8

    ```
    Don't forget to replace token here with your own token

4. Get all the connects
    ```
    curl -XGET http://127.0.0.1:5000/api/connects?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiYmlrYXNoIiwiZXhwIjoxNjU2MTU0MDY5fQ.3wmgfQfPNYUpdUh954rULKdKYgBzL8N0UAPnSu7Qxt8
    ```

5. Get detailed information about all connects
    ```
    curl -XGET http://127.0.0.1:5000/api/connects/info?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiYmlrYXNoIiwiZXhwIjoxNjU2MTU0MDY5fQ.3wmgfQfPNYUpdUh954rULKdKYgBzL8N0UAPnSu7Qxt8



