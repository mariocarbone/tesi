from flask import Flask
import subprocess
app = Flask(__name__)
 
@app.route("/")
def index():
    return "Please visit /shutdown or /restart"

@app.route("/restart")
def restart():
    subprocess.run("shutdown -r 0", shell=True, check=True)
    return "Restarting"

@app.route("/shutdown")
def shutdown():
    subprocess.run("shutdown -h 0", shell=True, check=True)
    return "Shutting down!"
 
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)