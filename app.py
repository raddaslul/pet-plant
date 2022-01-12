import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime, timedelta
import requests



app = Flask(__name__)

from pymongo import MongoClient
# 로그인때문에 DB에 보안이 필요함-> id, pw, ip주소 적용한 mongoDB연결코드
client = MongoClient('mongodb://13.209.77.90', 27017, username="test", password="test")
db = client.dbsparta
# client = MongoClient('localhost', 27017) # 로컬 사용 DB
# client = MongoClient('mongodb://test:test@localhost', 27017) # 서버 작동 DB

SECRET_KEY = 'SPARTA'


### 화면 보여주기 ###
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/shareplant')
def shareplant():
    return render_template('myplant.html')




### API ###
# 아이디 중복확인
@app.route('/member/userid_dup', methods=['POST'])
def check_dup():
    #js에서 필터링을 해서 통과한 값이 넘어옴
    userid_receive = request.form['userid_give']

    # DB에 넘어온 아이디를 찾아줌 : username이 findone이 된다면 bool값으로 true출력
    # 없으면 bool값으로 false출력됨 // find하는 db폴더이름 확인!!!
    exists = bool(db.userinfo.find_one({"userid": userid_receive}))
    print(userid_receive)
    return jsonify({'result': 'success', 'exists': exists})


# 회원가입
@app.route('/member/save', methods=['POST'])
def sign_up():
    userid_receive = request.form['userid_give']
    userpw_receive = request.form['userpw_give']

    #비밀번호 받아서 encode화 해준 뒤 저장
    password_hash = hashlib.sha256(userpw_receive.encode('utf-8')).hexdigest()
    doc = {
        "userid": userid_receive,                               # 아이디
        "userpw": password_hash,                                  # 비밀번호
        "profile_name": userid_receive,                           # 프로필 이름 기본값은 아이디
        "profile_pic": "",                                          # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png", # 프로필 사진 기본 이미지
        "profile_info": ""                                          # 프로필 한 마디
    }
    db.userinfo.insert_one(doc)
    return jsonify({'result': 'DB저장 success'})


# 로그인
@app.route('/login', methods=['POST'])
def sign_in():

    userid_receive = request.form['userid_give']
    userpw_receive = request.form['userpw_give']
    # print(userid_receive, userpw_receive)

    pw_hash = hashlib.sha256(userpw_receive.encode('utf-8')).hexdigest()
    result = db.userinfo.find_one({'userid': userid_receive, 'userpw': pw_hash})

    if result is not None:
        payload = {
         'id': userid_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token, 'id':userid_receive})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# my식물 보여주기
@app.route('/api/reg', methods=['GET'])
def show_reg():
    plant = list(db.pet_plant.find({}, {'_id': False}))
    return jsonify({'all_plants': plant})


# my식물 저장하기
@app.route('/api/reg', methods=['POST'])
def save_reg():
    name_receive = request.form['name_give']
    review_receive = request.form['review_give']

    file = request.files["file_give"]

    extension = file.filename.split('.')[-1]

    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

    filename = f'file-{mytime}'


    save_to = f'static/{filename}.{extension}'
    file.save(save_to)

    doc = {
        'name': name_receive,
        'review': review_receive,
        'file': f'{filename}.{extension}'
    }
    db.pet_plant.insert_one(doc)

    return jsonify({'msg': '저장을 완료하였습니다.'})


# my식물 삭제하기
@app.route('/api/delete', methods=['POST'])
def delete_review():
    name_recieve = request.form['name_give']

    db.pet_plant.delete_one({'name': name_recieve})

    return jsonify({'msg': '삭제가 완료되었습니다.'})





if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
