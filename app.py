import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_cors import CORS
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup


app = Flask(__name__)
CORS(app)

from pymongo import MongoClient
# client = MongoClient('localhost', 27017) # 로컬 사용 DB
client = MongoClient('mongodb://test:test@localhost', 27017) # 서버 작동 DB
db = client.dbsparta

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
    # print(userid_receive)
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


# 토큰받아서 만료시간 적용하는부분
#
# @app.route('/api/timeover', methods=['GET'])
# def tokenTime():
#     token_receive = request.cookies.get('mytoken')
#     try:
#         # token을 시크릿키로 디코딩합니다.
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#         print(payload)
#
#         # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
#         userinfo = db.userinfo.find_one({'userid': payload['id']}, {'_id': 0})
#         print(userinfo)
#
#         return jsonify({'result': '토큰있음', 'userid': userinfo['userid']})
#     except jwt.ExpiredSignatureError:
#         # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
#         return jsonify({'result': '로그인 만료', 'msg': '로그인 시간이 만료되었습니다.'})
#     except jwt.exceptions.DecodeError:
#         return jsonify({'result': '로그인 정보없음', 'msg': '로그인 정보가 존재하지 않습니다.'})


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


# search식물 검색기능
@app.route('/search')
def search():
    return render_template('searchplant.html')

@app.route('/searchplant', methods=['get'])
def searching_main():
    searchlist = []
    keyword = request.args.get('keyword_give')
    # print(keyword)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data_main = requests.get("https://www.fuleaf.com/search?term=" + keyword, headers=headers)
    # print(data_main)
    soup_main = BeautifulSoup(data_main.text, 'html.parser')
    # print(soup_main)
    plants_main = soup_main.select('#plants_list > ul > div')
    # print(plants_main)
    for plant in plants_main:
        imgs = plant.select_one('a > div.plant__image')
        # print(imgs)
        img_plants = str(imgs).split('url(')[1].split(');')[0]
        title_plants = plant.select_one('div.plant__title-flex > h3').text
        # print(img_plants, title_plants)

        code = str(plant).split('count/')[1].split('"><div')[0]
        data_desc = requests.get(f"https://www.fuleaf.com/plants/detail/{code}", headers=headers)
        soup_desc = BeautifulSoup(data_desc.text, 'html.parser')
        plants_descs = str(soup_desc).split('intro">')[1].split('</h3>')[0]
        # print(plants_descs)
        dict = {'img_plant': img_plants, 'title_plant': title_plants, 'plants_desc': plants_descs}
        # print(dict)
        searchlist.append(dict)
        print(searchlist)
    # print(img_plants, title_plants, plants_descs)
    return jsonify({'result' : searchlist})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
