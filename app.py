import os
from flask_scss import Scss
from flask import Flask,render_template,redirect,request,url_for
from gtts import gTTS
import gradio as gr
import speech_recognition as sr
from googletrans import Translator, constants
from pprint import pprint
from moviepy.editor import *
from werkzeug.utils import secure_filename
ALLOWED_EXTENSIONS = set(['mp4','','MPEG','WebM'])
UPLOAD_FOLDER = 'static/videos/'
AUDIO_FILE_UPLOAD ='/static/'
app=Flask(__name__)
Scss(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['AUDIO_FILE_UPLOAD'] = AUDIO_FILE_UPLOAD
# For session
SECRET_KEY     = "JbFjkRXU2yKvloxdfyxJABFHmhqGVYvIl7zxu0"
app.secret_key = SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
FLASK_DEBUG=1



def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def video_to_translate(file_obj,initial_language,final_language):
# Insert Local Video File Path
    videoclip = VideoFileClip(os.path.join(UPLOAD_FOLDER,file_obj))
    # Insert Local Audio File Path
    videoclip.audio.write_audiofile("test.wav",codec='pcm_s16le')
# initialize the recognizer
    r = sr.Recognizer()

    
    # open the file
    with sr.AudioFile("test.wav") as source:
        # listen for the data (load audio to memory)
        r.adjust_for_ambient_noise(source,duration=4)
        audio_data = r.record(source,offset=2)
        # recognize (convert from speech to text)
        text = r.recognize_google(audio_data, language = initial_language)

    
    # init the Google API translator
    translator = Translator()
    translation = translator.translate(text, dest=final_language)
    #translation.text
    trans=translation.text
    myobj = gTTS(text=trans, lang=final_language, slow=False) 
    myobj.save("audio.wav") 
    # loading audio file
    audioclip = AudioFileClip("audio.wav")
    
    # adding audio to the video clip
    new_audioclip = CompositeAudioClip([audioclip])
    videoclip.audio = new_audioclip
    new_video="static/videos/video_translated_"+final_language+".mp4"
    videoclip.write_videofile(new_video)
    #return 'audio.wav'
    return new_video

@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('upload'))
        userEmail = request.form['username']
        userPassword = request.form['password']
        return flask.redirect('/')
        
    return render_template("login.html")
    
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        return redirect(url_for('login'))
    return render_template("signup.html")
    
@app.route('/about', methods=['GET','POST'])
def about():
    return render_template('about.html')

@app.route('/service', methods=['GET','POST'])
def service():
    return render_template('service.html')

@app.route('/team', methods=['GET','POST'])
def team():
    return render_template('team.html')

@app.route('/contact', methods=['GET','POST'])
def contact():
    return render_template('contact.html')
@app.route("/upload", methods=["GET","POST"])
def upload():
    ret=0
    if request.method == "POST":
        if 'file' not in request.files:
            return render_template('upload.html', msg='No file selected')
        file = request.files['file']
        # if no file is selected
        if file.filename == '':
            return render_template('upload.html', msg='No file selected')
        if file and allowed_file(file.filename):
            initial_language=request.form.get("initial-language")
            final_language=request.form.get("final-language")
            filename2 = secure_filename(file.filename)
            file_location=os.path.join(UPLOAD_FOLDER, filename2)
            file.save(file_location)
            newvideo=video_to_translate(filename2,initial_language,final_language)
            return render_template('upload.html', Original_video=file_location,Translated_video=os.path.join(UPLOAD_FOLDER,"video_translated_{}.mp4".format(final_language)))
            
    elif request.method=='GET':
        return render_template('upload.html')

if __name__=='__main__':
    app.run(debug=True, port=5000)