import random
import re

from flask import Response
from flask import abort, jsonify
from flask import current_app
from flask import make_response
from flask import request

from info import sr
from info.constants import IMAGE_CODE_REDIS_EXPIRES, SMS_CODE_REDIS_EXPIRES
from info.libs.captcha.pic_captcha import captcha
from info.libs.yuntongxun.sms import CCP
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
@pass_blu.route("/get_sms_code", methods=["GET", "POST"])
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