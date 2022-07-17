import json
import sys
from datetime import datetime
import requests
from pprint import pprint
from itertools import groupby
import secure as secure
import yadisk
import vk

with open('token.txt', 'r') as file_object:
    token = file_object.read().strip()


class VK:

    def __init__(self, access_token, user_id, version='5.131', album_id='profile', extended='1'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.extended = extended
        self.album_id = album_id
        self.params = {'access_token': self.token, 'v': self.version}

    def users_photos(self):
        url = 'https://api.vk.com/method/photos.get'
        params = {'user_ids': self.id, 'album_id': self.album_id, 'extended': self.extended, 'photo_sizes': 1,
                  'count': count}
        response = (requests.get(url, params={**self.params, **params}).json())
        return response['response']['items']


# user_id = '17331357'
user_id = input("Введите ID пользователя VK: ")
session = vk.Session()
vk_api = vk.API(session)
check_ID = (vk_api.users.get(access_token=token, v='5.131', user_id=user_id))
if not check_ID:
    print("Нет такого ID!")
    sys.exit()
# count = 4
count = int(input("Введите количество скачиваемых фотографий: "))
access_token = token
vk = VK(access_token, user_id)

# pprint(vk.users_photos())

fotos_big_size = []
fotos_name = []
fotos_url = []
fotos_date = []
list_name_foto = []
size_foto = []
for i in vk.users_photos():
    fotos_name.append(list(i.get('likes').values()))
    fotos_date.append(i.get('date'))
    fotos_big_size.append(i.get('sizes')[-1])

for size in fotos_big_size:
    size_foto.append(size.get('type'))

for i in fotos_big_size:
    fotos_url.append(i.get('url'))

for foto_like in fotos_name:
    foto_name_like = str(foto_like[0]) + str(foto_like[1]) + '.jpg'
    list_name_foto.append(foto_name_like)

res = [val for key, grp in groupby(list_name_foto)
       for val in [key] + [False] * (len(list(grp)) - 1)]

for i, val in enumerate(res):
    if val == False:
        list_name_foto[i] = str(datetime.fromtimestamp(fotos_date[i]).date()) + '  ' + list_name_foto[i]

dictionary_foto = dict(zip(list_name_foto, fotos_url))

dict_file_name = {}
dict_size = {}
list_data_foto = []

for i in range(len(size_foto)):
    dict_file_name.clear()
    dict_size.clear()
    dict_file_name.setdefault('file_name', list_name_foto[i])
    dict_size.setdefault("size", size_foto[i])
    dict_json={**dict_file_name, **dict_size}
    list_data_foto.append(dict_json)

# with open("data_file.json", "w") as write_file:
#     json.dump(list_data_foto, write_file)


class YandexDisk:

    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def put_folder(self, folder_name):
        files_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.get_headers()
        params = {"path": folder_name}
        requests.put(files_url, params=params, headers=headers)
        pprint('Папка создана')

    def _get_upload_link(self, disk_file_path):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_headers()
        params = {"path": disk_file_path, "overwrite": "true"}
        response = requests.get(upload_url, headers=headers, params=params)
        return response.json()

    def upload_data_to_disk(self, disk_file_path, filename):
        href = self._get_upload_link(disk_file_path=disk_file_path).get("href", "")
        response = requests.put(href, data=filename)

    def upload_file_to_link(self, disk_file_path, url):
        href = self._get_upload_link(disk_file_path=disk_file_path).get("href", "")
        response = requests.put(href, data=url)
        print(f"Файл {keys} загружен")


# if __name__ == '__main__':
# TOKEN = "AQAAAAAJ2UEnAADLW_g9FsGOjUm9koH-YGtzlMs"
TOKEN = input("Введите токен Яндекс.Диск: ")
# user_id = '17331357'
check = yadisk.YaDisk(token=TOKEN)
# Проверяет, валиден ли токен
if check.check_token() == True:
    folder = input("Введите имя папки для сохранения фотографий: ")
    ya = YandexDisk(TOKEN)
    ya.put_folder(folder_name=folder)
    ya.upload_data_to_disk(f"{folder}/data_foto.json", list_data_foto)
    for keys, values in dictionary_foto.items():
        ya.upload_file_to_link(disk_file_path=f"{folder}/{keys}", url=values)
else:
    print("Некорректный токен!")


