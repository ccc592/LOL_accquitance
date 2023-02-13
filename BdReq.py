import base64

import requests

from ConfigUtils import my_config


class BdReq:
    def __init__(self):
        self.__api_key = my_config.get("base", "api_key")
        self.__secret_key = my_config.get("base", "secret_key")
        self.__access_token = "25.abfbd8a7dbec447727984717dc3a6e49.315360000.1990869678.282335-30169168"

    def refresh_token(self):
        host = f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={self.__api_key}&client_secret={self.__secret_key}'
        response = requests.get(host)
        if response:
            resp_json = response.json()
            self.__access_token = resp_json["access_token"]

    def request_ocr(self, image_path):
        self.refresh_token()
        # 读取图片并将图片转换为 base64 编码
        with open(image_path, "rb") as f:
            image = base64.b64encode(f.read())

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general"
        params = {
            "access_token": self.__access_token,
        }
        data = {
            "image": image,
        }

        response = requests.post(url, headers=headers, params=params, data=data)
        if response:
            resp_json = response.json()
            return resp_json
