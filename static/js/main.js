const mainBox = document.querySelector('.main_box');
const userLogin = document.querySelector('#user_login');
const userRegist = document.querySelector('#user_regist');
const mainLoginBtn = document.querySelector('.main_login_btn');
const HIDDEN = 'hidden';

//메인page에서 로그인 창 생성
function enter() {
    userLogin.classList.remove(HIDDEN)
    userRegist.classList.add(HIDDEN)
    mainLoginBtn.classList.add(HIDDEN)
}
//회원가입 창 생성
function regist_move() {
    userRegist.classList.remove(HIDDEN)
    userLogin.classList.add(HIDDEN)
    mainBox.classList.add(HIDDEN)
}
//로그인 창 생성
function login_move() {
    userLogin.classList.remove(HIDDEN)
    userRegist.classList.add(HIDDEN)
    mainBox.classList.add(HIDDEN)
}


// 정규표현식 id,pw조건
function is_nickname(asValue) {
    let regExp = /^(?=.*[a-zA-Z])[-a-zA-Z0-9_.]{4,12}$/;
    return regExp.test(asValue);
}

function is_password(asValue) {
    let regExp = /^(?=.*\d)(?=.*[a-zA-Z])[0-9a-zA-Z!@#$%^&*]{8,20}$/;
    return regExp.test(asValue);
}


// 아이디 중복확인
function userid_dup() {
    let userid = $("#user_regist .input_userid").val()
    // console.log(userid)

    //아이디입력 조건에 맞는지
    if (userid == "") {
        alert('아이디를 입력하세요');
        // console.log(userid)
        $("#user_regist .input_userid").focus();
        return;
    }
    //정규식에 내용이 포함되는지
    if (!is_nickname(userid)) {
        $(".op_id").text("아이디는 영문과 숫자, 길이 4-12자 이내")
        $("#user_regist .input_userid").focus()
        return;
    }

    $.ajax({
        type: "POST",
        url: "/member/userid_dup",
        data: {userid_give: userid},
        success: function (response) {
            // console.log(response["exists"])
            // console.log(response["result"])
            if(response["exists"]){
                alert("이미 존재하는 아이디입니다.")
                $("#user_regist .input_userid").val('')
                $("#user_regist .input_userid").focus()
            } else {
                alert("사용할 수 있는 아이디입니다.")
                $("#user_regist .input_userid").addClass("is-success")
                $("#user_regist .input_userpw").focus()
            }
        }
    })
}

// 회원가입
function regist() {
    let userid = $("#user_regist .input_userid").val()
    let userpw = $("#user_regist .input_userpw").val()
    let userpw_re = $("#user_regist .input_userpw_re").val()
    // console.log(userid, userpw, userpw_re)

    // id 중복확인버튼눌렀는지 확인
    if (!$("#user_regist .input_userid").hasClass("is-success")) {
        alert("아이디 중복확인을 해주세요.")
        return;
    }
    //pw 빈칸인지 , 정규식통과했는지, 다 통과됐으면 pass
    if (userpw == "") {
        alert("비밀번호를 입력해주세요")
        $("#user_regist .input_userpw").focus()
        return;
    } else if (!is_password(userpw)) {
        alert("비밀번호의 형식을 확인해주세요. 영문과 숫자 필수 포함, 특수문자(!@#$%^&*) 사용가능 8-20자")
        $("#user_regist .input_userpw").focus()
        return
    } else {
        $(".op_pw").text("사용할 수 있는 비밀번호입니다.")
        $('#user_regist .input_userpw').addClass("is-success")
    }

    // pw_re 빈칸인지, pw1이랑 똑같은지 , 똑같으면 pass
    if (userpw_re == "") {
        alert("비밀번호 확인을 입력해주세요.")
        $(".input_userpw_re").focus()
        return;
    } else if (userpw_re != userpw) {
        alert("비밀번호가 일치하지 않습니다.")
        $(".op_pw_re").text('비밀번호가 일치하지 않습니다')
        $(".input_userpw_re").val('')
        $(".input_userpw_re").focus()
        return;
    } else {
        $(".op_pw_re").text("비밀번호가 일치합니다.")
        $('.input_userpw_re').addClass("is-success")
    }

    // 위에 if문들 통과했으면 변수에 자료 담아서 app.py로 보냄
    $.ajax({
        type: "POST",
        url: "/member/save",
        data: {
            userid_give: userid,
            userpw_give: userpw
        },
        success: function (response) {
            alert("회원가입을 축하드립니다!")
            console.log(response['result'])
            if ($('#user_login').css('display') =='none'){
                $('#user_login').show();
                $('#user_login .input_userid').val('');
                $('#user_login .input_userpw').val('');
                $('#user_regist').hide();
            }
        }
    });
}

// 로그인
function login() {
    let userid = $("#user_login .input_userid").val()
    let userpw = $("#user_login .input_userpw").val()

    if (userid == "") {
        alert("아이디를 입력해주세요.")
        $("#user_login .input_userid").focus()
        return;
    }
    if (userpw == "") {
        alert("비밀번호를 입력해주세요.")
        $("#user_login .input_userpw").focus()
        return;
    }

    $.ajax({
        type: "POST",
        url: "/login",
        data: {
            userid_give: userid,
            userpw_give: userpw
        },
        success: function (response) {
            console.log(response['result'])
            let userid = (response['id'])
            if (response['result'] == 'success') {
                $.cookie('mytoken', response['token'], {path: '/'});
                //토큰이름 , 토큰값
                if ($('.welcome').css('display') == 'none') {
                    $('.welcome').show();
                    $('#user_login').hide();
                    // window.location.replace("/") 페이지이동
                    let welcome_user = `<span class="welcome_userid"> ${userid}님 </span>`
                    $('.welcome_title').append(welcome_user)
                }
                if ($('nav .user_box').css('display')=='none'){
                    $('nav .user_box').show();
                    let nav_user = `<sapn class="nav_userid">${userid}님</sapn>`
                    $('nav .user_box a.user').append(nav_user)
                }
            } else {
                alert(response['msg'])
                $(".input_userpw").val('')
                $(".input_userid").val('')
                $(".input_userid").focus()
            }
        }
    })
}

// 로그아웃
function logout(){
    $.removeCookie('mytoken', {path: '/'});
    window.location.href = '/';
}

 // 토큰받아서 만료시간 데이터받는
$(document).ready(function () {
          tokenTime();
});

function tokenTime() {
  $.ajax({
      type: "GET",
      url: "/api/timeover",
      data: {},
      success: function (response) {
          console.log(response["result"]);
      }
  })
}
