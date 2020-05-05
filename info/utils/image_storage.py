# -*- coding: utf-8 -*-
# flake8: noqa

import qiniu.config
from qiniu import Auth, etag, put_data, put_file

access_key = 'O_bTSx56jUGypUp4QmRXdFlwZkBXakBSexhWBpTA'
secret_key = 'Dcr8yDYHeYkGc8hC7GjW_i2dm5oAGe_NiMPZjwev'


def image_storage(file_data):
    """
    存储图片到七牛服务器
    :param file_data: 文件二进制码
    :return:
    """
    q = Auth(access_key, secret_key)

    bucket_name = 'ihome-python-why2'

    # # 上传文件到七牛后， 七牛将文件名和文件大小回调给业务服务器。
    # policy = {
    #     'callbackUrl': 'http://your.domain.com/callback.php',
    #     'callbackBody': 'filename=$(fname)&filesize=$(fsize)'
    # }

    token = q.upload_token(bucket_name, None, 3600)

    # localfile = '../static/images/home01.jpg'
    # ret, info = put_file(token, None, localfile)

    ret, info = put_data(token, None, file_data)

    if info.status_code == 200:
        return ret.get('key')
    else:
        raise Exception('上传图片失败')


if __name__ == "__main__":
    with open('../static/images/home01.jpg', 'rb') as f:
        file_data = f.read()
        image_storage(file_data)
