from flask import Flask, escape, request, render_template
from threading import Timer, Lock

app = Flask(__name__)
app.config['EXPIRE_TIME'] = 60.0

session_map = {}
session_lock = Lock()

ERR_NO_SESSION = 1
ERR_NO_OTP = 2

@app.get('/new_session/<sid>')
def new_session(sid):
    session_map[sid] = None

    def clear():
        with session_lock:
            if sid in session_map:
                session_map.pop(sid)

    Timer(app.config['EXPIRE_TIME'], clear).start()
    return { "Sucess": True }

@app.get('/upload_otp/<sid>/<otp>')
def upload(sid, otp):
    with session_lock:
        if sid in session_map:
            session_map[sid] = otp
            return { "Success": True }
        else:
            return { "Success": False, "Code": ERR_NO_SESSION }

@app.get('/get_otp/<sid>')
def get_otp(sid):
    with session_lock:
        if sid in session_map:
            if session_map[sid] is not None:
                otp = session_map.pop(sid)
                return { "Success": True, "OTP": otp }
            else:
                return { "Success": False, "Code": ERR_NO_OTP }
        else:
            return { "Success": False, "Code": ERR_NO_SESSION }

@app.get('/upload/<otp>')
def entry(otp):
    return render_template("upload.html", sessions=session_map.keys(), otp=otp)

if __name__ == "__main__":
    app.run(debug=True)
