from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
# client = MongoClient('mongodb://test:test@localhost', 27017)
db = client.dbsparta

from datetime import datetime

@app.route('/')
def home():
    return render_template('index.html')

#my식물 보여주기
@app.route('/api/reg', methods=['GET'])
def show_reg():
    plant = list(db.pet_plant.find({}, {'_id': False}))
    return jsonify({'all_plants': plant})

#my식물 저장하기
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

#my식물 삭제하기
@app.route('/api/delete', methods=['POST'])
def delete_review():
    name_recieve = request.form['name_give']

    db.pet_plant.delete_one({'name': name_recieve})

    return jsonify({'msg': '삭제가 완료되었습니다.'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
