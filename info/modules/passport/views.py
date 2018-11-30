from flask import Response
from flask import abort, jsonify
from flask import current_app
from flask import make_response
from flask import request

from info import sr
from info.constants import IMAGE_CODE_REDIS_EXPIRES
from info.libs.captcha.pic_captcha import captcha
from info.modules.passport import pass_blu




# 登陆注册页面
# 获取图片验证码
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