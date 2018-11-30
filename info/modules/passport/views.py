import random
import re
from datetime import datetime

from flask import Response
from flask import abort, jsonify
from flask import current_app
from flask import make_response
from flask import request
from flask import session

from info import sr, db
from info.constants import IMAGE_CODE_REDIS_EXPIRES, SMS_CODE_REDIS_EXPIRES
from info.libs.captcha.pic_captcha import captcha
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.modules.passport import pass_blu




# 登陆注册页面
# 获取图片验证码
from info.utils.response_code import RET, error_map


@pass_blu.route("/get_img_code")
def get_img_code():
    # 获取参数
    img_code_id = request.args.get("img_code_id")

    # 校验参数
    if not img_code_id:
        return abort(403)

    # 生成图片验证码
    img_name, img_code, img_bytes = captcha.generate_captcha()
    # 保存图图片验证码
    try:
        sr.set("img_code_id_" + img_code_id, img_code, ex=IMAGE_CODE_REDIS_EXPIRES)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(500)

    # 返回图片　自定义响应对象
    response = make_response(img_bytes)   # type:Response
    response.content_type = "image/jpeg"
    # 返回数据
    return response


# 获取短信验证码
@pass_blu.route("/get_sms_code", methods=["POST"])
def get_sms_code():
    # 获取参数
    img_code_id = request.json.get("img_code_id")
    img_code = request.json.get("img_code")
    mobile = request.json.get("mobile")
    # 校验参数
    if not all([img_code, img_code_id, mobile]):
            return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    #　校验手机号格式
    if not re.match(r"^1[345678]\d{9}$", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 判断用户是否存在　从数据库查找数据
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg=error_map[RET.DATAEXIST])
    # 用户已经注册过
    if user:
        return jsonify(errno=RET.DATAEXIST, errmsg=error_map[RET.DATAEXIST])

    # 从redis中取出数据校验参数
    try:
        real_img_code = sr.get("img_code_id_" + img_code_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])
    # 校验图片验证码
    if real_img_code != img_code.upper():
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 生成随机四位数字
    rand_num =  "%04d" % random.randint(0, 9999)

    # 生成短信验证码
    # response_code = CCP().send_template_sms(mobile, [rand_num, 5], 1)
    # if response_code != 0:
    #     return jsonify(errno=RET.THIRDERR, errmsg=error_map[RET.THIRDERR])

    # 保存短信验证码
    try:
        sr.set("sms_code_id_" + mobile, rand_num, ex=SMS_CODE_REDIS_EXPIRES)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    # 打印短信验证码
    current_app.logger.info("sms_code:%s" % rand_num)
    # 返回数据
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 用户注册
@pass_blu.route("/register", methods=["POST"])
def register():
    # 获取参数
    sms_code = request.json.get("sms_code")
    mobile = request.json.get("mobile")
    password = request.json.get("password")
    # 校验参数
    if not all([sms_code, mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 　校验手机号格式
    if not re.match(r"^1[345678]\d{9}$", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 校验短信验证码
    try:
        real_sms_code = sr.get("sms_code_id_" + mobile)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    if real_sms_code != sms_code:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    # 保存用户信息
    try:
        user = User()
        user.mobile = mobile
        user.nick_name = mobile
        # 封装加密过程
        user.password = password
        # 记录最后登陆时间
        user.last_login = datetime.now()
        db.session.add(user)
        db.session.commit()
    except BaseException as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    # 状态保持
    session["user_id"] = user.id

    # 返回结果
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 登陆入口
@pass_blu.route("/login", methods=["POST"])
def login():
    # 获取参数
    mobile = request.json.get("mobile")
    password = request.json.get("password")
    # 校验参数
    if not all([mobile, password]):
            return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 　校验手机号格式
    if not re.match(r"^1[345678]\d{9}$", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 查询数据
    user = None
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    # 判断用户是否存在
    if not user:
        return jsonify(errno=RET.NODATA, errmsg=error_map[RET.NODATA])

    if not user.check_password(password):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 状态保持
    session["user_id"] = user.id

    # 记录最后登陆时间
    user.last_login = datetime.now()

    # 返回结果
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])