

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login
import datetime
import re
import urllib, cStringIO


from werkzeug import secure_filename
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Yaolan126126'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()

def getUserList():
    cursor = conn.cursor()
    cursor.execute("SELECT email from Users")
    return cursor.fetchall()

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):
    users = getUserList()
    if not(email) or email not in str(users):
        return
    user = User()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    users = getUserList()
    email = request.form.get('email')
    if not(email) or email not in str(users):
        return
    user = User()
    user.id = email
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
    data = cursor.fetchall()
    pwd = str(data[0][0] )
    user.is_authenticated = request.form['password'] == pwd
    return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
    return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return '''
               <form action='login' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'></input>
                <input type='password' name='password' id='password' placeholder='password'></input>
                <input type='submit' name='submit'></input>
               </form></br>
	       <a href='/'>Home</a>
               '''
    #The request method is POST (page is recieving data)
    email = flask.request.form['email']
    cursor = conn.cursor()
    #check if email is registered
    if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
        data = cursor.fetchall()
        pwd = str(data[0][0] )
        if flask.request.form['password'] == pwd:
            user = User()
            user.id = email
            flask_login.login_user(user) #okay login in user
            return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

    #information did not match
    return "<a href='/login'>Try again</a>\
            </br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('protected'))
    #return render_template('hello.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():

    return render_template('register.html', supress='True')


@app.route("/register", methods=['POST'])
def register_user():
    try:
        email=request.form.get('email')
        password=request.form.get('password')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        dob = request.form.get('dob')
        hometown = request.form.get('hometown')
        gender = request.form.get('gender')
    except:
        print "couldn't find all tokens" #this prints to shell, end users will not see this (all print statements go to shell)
        return flask.redirect(flask.url_for('register'))
    cursor = conn.cursor()
    test =  isEmailUnique(email)
    if test:
        print cursor.execute("INSERT INTO Users (fname, lname, email, dob, hometown, gender, password) VALUES ('{0}', '{1}', '{2}', '{3}','{4}', '{5}', '{6}')".format(fname, lname, email, dob, hometown, gender, password))
        conn.commit()
        #log user in
        user = User()
        user.id = email
        flask_login.login_user(user)
        user_id = getUserIdFromEmail(flask_login.current_user.id)
        #cursor.execute("INSERT INTO friends (friend_one, friend_two, status) VALUES ('{0}', '{1}', '{2}')".format(user_id, user_id, 2))
        return render_template('hello.html', name=email, message='Account Created!')
    else:
        print "couldn't find all tokens"
        return flask.redirect(flask.url_for('register'))

#def getUsersPhotos(uid):
#    cursor = conn.cursor()
#    cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = '{0}'".format(uid))
#    return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]
def getDoBfromUser(user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT dob FROM Users WHERE user_id = '{0}'".format(user_id))
    return cursor.fetchone()[0]
def getGenderfromUser(user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT gender FROM Users WHERE user_id = '{0}'".format(user_id))
    return cursor.fetchone()[0]
def gethometownfromUser(user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT hometown FROM Users WHERE user_id = '{0}'".format(user_id))
    return cursor.fetchone()[0]
def getemailfromUser(user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM Users WHERE user_id = '{0}'".format(user_id))
    return cursor.fetchone()[0]

def getAlbumPhotos(album_id):
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures_Album WHERE album_id = '{0}'".format(album_id))
    return cursor.fetchall()
def getPicturedatafromPictureId(picture_id):
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata FROM Pictures_Album WHERE picture_id = '{0}'".format(picture_id))
    return cursor.fetchone()[0]
def getTagPictures(tag_id):
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata, picture_id FROM Picture_tags WHERE tag_id = '{0}'".format(tag_id))
    return cursor.fetchall()

def getUsersAlbum(user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT alname FROM Albums_own WHERE user_id = '{0}'".format(user_id))
    alname = []
    allname = cursor.fetchall()
    for name in allname:
        alname.append(name[0])
    return alname

def getAlbumIdFromAlname(alname):
    cursor = conn.cursor()
    cursor.execute("SELECT album_id FROM Albums_own WHERE alname = '{0}'".format(alname))
    return cursor.fetchone()[0]
def getPictureIdFromimgdata(imgfile):
    cursor = conn.cursor()
    cursor.execute("SELECT picture_id FROM Pictures_Album WHERE imgdata = '{0}'".format(imgfile))
    return cursor.fetchone()[0]
def getTagIdFromTag(tag):
    cursor = conn.cursor()
    cursor.execute("SELECT tag_id FROM Tag WHERE tag = '{0}'".format(tag))
    return cursor.fetchone()[0]

def getUserIdFromEmail(email):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]

def isEmailUnique(email):
    #use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
        #this means there are greater than zero entries with that email
        return False
    else:
        return True
#end login code

def getAlltags():
    tags=[]
    tags.append('human')
    tags.append('science')
    tags.append('sightseeing')
    tags.append('animal')
    tags.append('universe')
    tags.append('plant')
    tags.append('cartoon')
    return tags
def AllAlbumPicture():
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata FROM Pictures_Album")
    al_picture = []
    data = cursor.fetchall()
    for picture in data:
        al_picture.append(picture[0])
    return al_picture
def AllUsersemail():
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM Users")
    al_email = []
    data = cursor.fetchall()
    for email in data:
        al_email.append(email[0])
    return al_email
def AllUsershometown():
    cursor = conn.cursor()
    cursor.execute("SELECT hometown FROM Users")
    al_hometown = []
    data = cursor.fetchall()
    for hometown in data:
        al_hometown.append(hometown[0])
    return al_hometown
def AllUsersgender():
    cursor = conn.cursor()
    cursor.execute("SELECT gender FROM Users")
    al_gender = []
    data = cursor.fetchall()
    for gender in data:
        al_gender.append(gender[0])
    return al_gender
def getFriendFromUserID(user_id):
    cursor = conn.cursor()
    friends_id = []
    cursor.execute("SELECT friend_one FROM friends WHERE friend_two='{0}'".format(user_id))
    data = cursor.fetchall()
    for friend in data:
        friends_id.append(friend[0])
    cursor.execute("SELECT friend_two FROM friends WHERE friend_one = '{0}'".format(user_id))
    data2 = cursor.fetchall()
    for friend in data2:
        friends_id.append(friend[0])
    friend_name = []
    for friend in friends_id:
        friend_name.append(getemailfromUser(friend))
    return friend_name



@app.route('/profile')
@flask_login.login_required
def protected():
    user_id = getUserIdFromEmail(flask_login.current_user.id)
    return render_template('profile.html', name=flask_login.current_user.id, dob=getDoBfromUser(user_id), gender=getGenderfromUser(user_id), email=getemailfromUser(user_id), hometown=gethometownfromUser(user_id), message='Here is your profile')
@app.route('/poptagpic')
@flask_login.login_required
def poptagpic():
    cursor = conn.cursor()
    cursor.execute("SELECT tag_id FROM Picture_tags GROUP BY tag_id ORDER BY COUNT(*) DESC LIMIT 1")
    tag_id = cursor.fetchone()[0]
    conn.commit()
    cursor.execute("SELECT tag FROM Tag WHERE tag_id = '{0}'".format(tag_id))
    tag = cursor.fetchone()[0]
    return render_template('tag.html', tagalbums = tag, photos = getTagPictures(tag_id))
@app.route('/youmayalsolike')
@flask_login.login_required
def youmayalsolike():
    user_id = getUserIdFromEmail(flask_login.current_user.id)
    cursor = conn.cursor()
    cursor.execute("SELECT tag_id FROM Picture_tags WHERE user_id = '{0}' GROUP BY tag_id ORDER BY COUNT(*) DESC LIMIT 1".format(user_id))
    tag_id = cursor.fetchone()[0]
    cursor.execute("SELECT tag FROM Tag WHERE tag_id = '{0}'".format(tag_id))
    tag = cursor.fetchone()[0]
    photo = getTagPictures(tag_id)
    return render_template('youmayalsolike.html', photos = photo, tagalbums = tag)

def getAllphotos():
    cursor = conn.cursor()
    cursor.execute("SELECT picture_id, imgdata, num_likes FROM Pictures_Album")
    pictures = cursor.fetchall()
    conn.commit()
    return pictures
@app.route('/allpicture')
#@flask_login.login_required
def allpicture():
    pictures = getAllphotos()
    return render_template('allpicture.html', photos = pictures, message='Here are all the photos uploaded through our website!')
#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
@app.route('/alluserpicture')
@flask_login.login_required
def alluserpicture():
    user_id = getUserIdFromEmail(flask_login.current_user.id)
    cursor = conn.cursor()
    cursor.execute("SELECT picture_id, imgdata FROM Pictures_Album WHERE user_id = '{0}'".format(user_id))
    photo = cursor.fetchall()
    return render_template('deletepicture.html', photos = photo, message = 'Delect the photos from your photo collection.')


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS



@app.route('/createalbum', methods=['GET', 'POST'])
@flask_login.login_required
def createalbum():
    if request.method == 'POST':
        user_id = getUserIdFromEmail(flask_login.current_user.id)
        alname = request.form.get('alname')
        print alname
        docreation = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        print docreation
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Albums_own (alname, docreation, user_id) VALUES ('{0}', '{1}', '{2}')".format(alname, docreation, user_id))
        conn.commit()
        return render_template('hello.html', name=flask_login.current_user.id, message='Album Created!', albums=getUsersAlbum(user_id))
    else:
        return render_template('createalbum.html', Albumc='True')



@app.route('/tagcollect', methods = ['GET', 'POST'])
@flask_login.login_required
def tagcollect():
    if request.method == 'POST':
        tagread = request.form.get('tagnname')
        print("tagread is" + tagread)
        tag_id = getTagIdFromTag(tagread)
        return render_template('tag.html', tagalbums=tagread, photos = getTagPictures(tag_id))
    else:
        return render_template('tagcollect.html', tags=getAlltags())
@app.route('/usertagcollect', methods = ['GET', 'POST'])
@flask_login.login_required
def usertagcollect():
    if request.method == 'POST':
        user_id = getUserIdFromEmail(flask_login.current_user.id)
        cursor = conn.cursor()
        tagread = request.form.get('tagnname')
        tag_id = getTagIdFromTag(tagread)
        cursor.execute("SELECT imgdata FROM Picture_tags WHERE user_id = '{0}'AND tag_id = '{1}'".format(user_id, tag_id))
        photo_data = cursor.fetchall()
        return render_template('usertag.html', tagalbums=tagread, photos = photo_data)
    else:
        return render_template('usertagcollect.html', tags=getAlltags())




@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
    if request.method == 'POST':
        user_id = getUserIdFromEmail(flask_login.current_user.id)
        add_score(user_id)
        alname = request.form.get('album_name')
        album_id = getAlbumIdFromAlname(alname)
        imgfile = request.files['photo']
        photo_data = base64.standard_b64encode(imgfile.read())
        caption = request.form.get('caption')
        tagread = request.form.get('tag_name')
        print("tagread in upload:" + tagread)
        tag_id = getTagIdFromTag(tagread)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Pictures_Album (user_id, imgdata, caption, album_id) VALUES ('{0}', '{1}', '{2}', '{3}')".format(user_id, photo_data, caption, album_id))
        picture_id = getPictureIdFromimgdata(photo_data)
        cursor.execute("INSERT INTO Picture_tags (imgdata, user_id, picture_id, tag_id) VALUES ('{0}', '{1}', '{2}', '{3}')".format(photo_data, user_id, picture_id, tag_id))
        conn.commit()
        return render_template('uploaded.html', name=flask_login.current_user.id, albums = alname, message='Photo uploaded!', photos=getAlbumPhotos(album_id) )
    else:
        return render_template('upload.html', name=flask_login.current_user.id, albums=getUsersAlbum(getUserIdFromEmail(flask_login.current_user.id)),  tags=getAlltags())

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method =='POST':
        search = request.form.get('search')
        #print(search)
        search2 = search.split("#")
        #print(search2[1])
        cursor = conn.cursor()
        tag_ids = []
        for i in range(len(search2)):
            #cursor.execute("SELECT tag_id FROM Tag WHERE tag = '{0}'".format(search2[i]))
            #tag_id = cursor.fetchone()[0]
            tag_ids.append(getTagIdFromTag(search2[i]))
        print(tag_ids)
        photo1 = getTagPictures(tag_ids[0])
        photo2 = getTagPictures(tag_ids[1])
        return render_template('searched.html', photos1 = photo1, photos2 = photo2, tag = search2)
    else:
        return render_template('search.html')
#end photo uploading code
@app.route('/albumcollect', methods=['GET', 'POST'])
@flask_login.login_required
def albumcollect():
    if request.method =='POST':
        alname = request.form.get('album_name')
        album_id = getAlbumIdFromAlname(alname)
        return render_template('album.html', name=flask_login.current_user.id, albums = alname, photos=getAlbumPhotos(album_id))
    else:
        return render_template('albumcollect.html', albums=getUsersAlbum(getUserIdFromEmail(flask_login.current_user.id)))

@app.route('/deletealbum', methods = ['GET', 'POST'])
@flask_login.login_required
def deletealbum():
    if request.method == 'POST':
        alname = request.form.get('album_name')
        album_id = getAlbumIdFromAlname(alname)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Albums_own WHERE album_id='{0}'".format(album_id))
        conn.commit()
        return render_template('deletealbum.html', message='You delete the album successfully', albums=getUsersAlbum(getUserIdFromEmail(flask_login.current_user.id)))
    else:
        return render_template('deletealbum.html', albums=getUsersAlbum(getUserIdFromEmail(flask_login.current_user.id)))

@app.route('/addfriend', methods=['GET', 'POST'])
@flask_login.login_required
def addfriend():
    if request.method == 'POST':
        user_id = getUserIdFromEmail(flask_login.current_user.id)
        friends = getFriendFromUserID(user_id)
        friendemail = request.form.get('friendemail')
        if friendemail == flask_login.current_user.id:
            return render_template('addfriend.html', message='You cannot add yourself as friends!', useremail=AllUsersemail())
        elif friendemail in friends:
            return render_template('addfriend.html', message='You two have already been friends, add another one!', useremail=AllUsersemail())
        else:
            friend_id = getUserIdFromEmail(friendemail)
            user_id = getUserIdFromEmail(flask_login.current_user.id)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO friends (friend_one, friend_two) VALUES ('{0}', '{1}')".format(user_id, friend_id))
            conn.commit()
            return render_template('friend.html', message='friends added and here are your friends!', friends=getFriendFromUserID(user_id))
    else:
        return render_template('addfriend.html', useremail=AllUsersemail())
@app.route('/friend')
def friend():
    user_id = getUserIdFromEmail(flask_login.current_user.id)
    return render_template('friend.html', friends=getFriendFromUserID(user_id), message='Friends')

def add_score(user_id):
    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET score = score + 1 WHERE user_id = '{0}'".format(user_id))
    conn.commit()
def add_like(picture_id):
    cursor = conn.cursor()
    cursor.execute("UPDATE Pictures_Album SET num_likes = num_likes + 1 WHERE picture_id = '{0}'".format(picture_id))
    conn.commit()
@app.route('/like/<picture_id>', methods=['POST', 'GET'])
def like(picture_id):
    #user_id = getUserIdFromEmail(flask_login.current_user.id)
    user_email = flask_login.current_user.id
    add_like(picture_id)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Picture_Like (picture_id, liker_email) VALUES ('{0}', '{1}')".format(picture_id, user_email))
    conn.commit()
    return render_template('allpicture.html', message = 'You liked a photo', photos=getAllphotos())

@app.route('/like_email/<picture_id>', methods = ['POST', 'GET'])
def like_email(picture_id):
    cursor = conn.cursor()
    cursor.execute("SELECT liker_email FROM Picture_Like WHERE picture_id = '{0}'".format(picture_id))
    likes_email = cursor.fetchall()
    like_email = []
    for likeemail in likes_email:
        like_email.append(likeemail[0])
    conn.commit()
    return render_template('like_collect.html', message = 'Here are the users who like this photo', photo = getPicturedatafromPictureId(picture_id), likes_email = like_email)
@app.route('/picture_delete/<picture_id>', methods=['POST', 'GET'])
def picture_delete(picture_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Pictures_Album WHERE picture_id = '{0}'".format(picture_id))
    conn.commit()
    user_id = getUserIdFromEmail(flask_login.current_user.id)
    cursor.execute("SELECT picture_id, imgdata FROM Pictures_Album WHERE user_id = '{0}'".format(user_id))
    photo = cursor.fetchall()
    return render_template('deletepicture.html', message='You have deleted your photo', photos = photo)

@app.route('/picture_comment/<picture_id>', methods=['POST', 'GET'])
def picture_comment(picture_id):

    user_id = getUserIdFromEmail(flask_login.current_user.id)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM Picture_tags WHERE picture_id = '{0}'".format(picture_id))
    owner_id = cursor.fetchone()[0]
    if request.method == 'POST':
        cotext = request.form.get('commenttt')
        dohave = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')

        if owner_id != user_id:
            cursor.execute("INSERT INTO Comments_photo (cotext, dohave, user_id, picture_id, owner_id) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')".format(cotext, dohave, user_id, picture_id, owner_id))
            return render_template('allpicture.html', message = 'Thank you for your comment!', photos = getAllphotos())
        else:

            return render_template('allpicture.html', message = 'You can not comment your own photo!', photos = getAllphotos())
    else:

        add_score(owner_id)
        return render_template('picture_comment.html', pid = picture_id)

@app.route('/comment_collect/<picture_id>', methods = ['POST', 'GET'])

def comment_collect(picture_id):
    cursor = conn.cursor()
    cursor.execute("SELECT cotext, user_id, dohave FROM Comments_photo WHERE picture_id = '{0}'".format(picture_id))
    commmessage = cursor.fetchall()
    comments2 = []
    for comment in commmessage:
        comments2.append(comment)
    conn.commit()

    return render_template('comment_collect.html', message = 'Here are the comments of this photo', photo = getPicturedatafromPictureId(picture_id), comments = comments2)

@app.route('/popuser', methods = ['GET', 'POST'])
def popuser():
    if request.method == 'POST':
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM Users GROUP BY user_id ORDER BY score DESC LIMIT 1")
        user_id = cursor.fetchone()[0]
        conn.commit()
        return render_template('popuser.html', useremail = getemailfromUser(user_id))
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM Users GROUP BY user_id ORDER BY score DESC LIMIT 1")
        user_id = cursor.fetchone()[0]
        conn.commit()
        return render_template('popuser.html', useremail = getemailfromUser(user_id))

@app.route('/poptag', methods=['GET', 'POST'])
def poptag():
    if request.method == 'POST':
        cursor = conn.cursor()
        cursor.execute("SELECT tag_id FROM Picture_tags GROUP BY tag_id ORDER BY COUNT(*) DESC LIMIT 1")
        tag_id = cursor.fetchone()[0]
        #print(tag_id)
        conn.commit()
        cursor.execute("SELECT tag FROM Tag WHERE tag_id = '{0}'".format(tag_id))
        tag = cursor.fetchone()[0]
        return render_template('tag.html', tagalbums = tag, photos = getTagPictures(tag_id))
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT tag_id FROM Picture_tags GROUP BY tag_id ORDER BY COUNT(*) DESC LIMIT 1")
        tag_id = cursor.fetchone()[0]
        #print(tag_id)
        conn.commit()
        cursor.execute("SELECT tag FROM Tag WHERE tag_id = '{0}'".format(tag_id))
        tag = cursor.fetchone()[0]
        return render_template('poptag.html', tagalbums = tag, photos = getTagPictures(tag_id))
def getallphotosfromuserId(user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT album_id FROM Albums_own WHERE user_id = '{0}'".format(user_id))
    album_ids = cursor.fetchall()
    album_id = []
    for albumid in album_ids:
        album_id.append(albumid[0])
    imgdatas=[]
    for i in range(len(album_id)):
        cursor.execute("SELECT picture_id FROM Pictures_Album WHERE album_id = '{0}'".format(album_id[i]))
        picture_ids = cursor.fetchall()
        for picture_id in picture_ids:
            imgdatas.append(getPicturedatafromPictureId(picture_id[0]))
    return imgdatas
@app.route("/popphoto")
def popphoto():
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM Users GROUP BY user_id ORDER BY score DESC LIMIT 1")
    user_id = cursor.fetchone()[0]
    useremail = getemailfromUser(user_id)
    conn.commit()
    photo = getallphotosfromuserId(user_id)
    return render_template('popphotocollect.html', photos = photo, popuser = useremail)
#default page
@app.route("/", methods=['GET'])
def hello():
    return render_template('hello.html', message='Welecome to Photoshare')

if __name__ == "__main__":
    #this is invoked when in the shell  you run
    #$ python app.py
    app.run(port=5000, debug=True)
