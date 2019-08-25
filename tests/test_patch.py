import unittest
import requests
from datetime import datetime
from copy import deepcopy


url = "http://localhost:8080"


class MyTestCase(unittest.TestCase):
    def check_import(self, import_id, data):
        response = requests.get(url + f"/imports/{import_id}/citizens")
        self.assertEqual(response.status_code, 200)
        for i in response.json()['data']:
            datetime.strptime(i['birth_date'], "%d.%m.%Y")
        self.assertDictEqual(data, response.json())

    def test_p_patch_one_req(self):
        data = {"citizens": [
            {"citizen_id": 1, "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7,
             "name": "Иванов Иван Иванович", "birth_date": "26.12.1986", "gender": "male", "relatives": []}
        ]}
        response = requests.post(url + "/imports", json=data)
        self.assertEqual(response.status_code, 201)
        import_id = response.json()['data']['import_id']

        data['data'] = deepcopy(data['citizens'])
        del data['citizens']

        data['data'][0]['town'] = "Дубовец"
        data['data'][0]['birth_date'] = "11.11.1999"

        upd = deepcopy(data['data'][0])
        del upd['citizen_id']
        response = requests.patch(url + f"/imports/{import_id}/citizens/1", json=upd)
        self.assertEqual(response.status_code, 200)
        upd = deepcopy(data['data'][0])
        self.assertDictEqual(upd, response.json()['data'])

        self.check_import(import_id, data)

    def test_p_patch_jo(self):
        data = {"citizens": [
            {"citizen_id": 1, "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7,
             "name": "Иванов Иван Иванович", "birth_date": "26.12.1986", "gender": "male", "relatives": []}
        ]}
        response = requests.post(url + "/imports", json=data)
        self.assertEqual(response.status_code, 201)
        import_id = response.json()['data']['import_id']

        data['data'] = deepcopy(data['citizens'])
        del data['citizens']

        data['data'][0]['town'] = "ё"
        data['data'][0]['birth_date'] = "11.11.1999"

        upd = deepcopy(data['data'][0])
        del upd['citizen_id']
        response = requests.patch(url + f"/imports/{import_id}/citizens/1", json=upd)
        self.assertEqual(response.status_code, 200)
        upd = deepcopy(data['data'][0])
        self.assertDictEqual(upd, response.json()['data'])

        self.check_import(import_id, data)

    def test_p_patch_rel(self):
        data = {"citizens": [
            {"citizen_id": 1, "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7,
             "name": "Иванов Иван Иванович", "birth_date": "26.12.1986", "gender": "male", "relatives": [2]},
            {"citizen_id": 2, "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7,
             "name": "Иванов Сергей Иванович", "birth_date": "17.04.1997", "gender": "male", "relatives": [1]},
            {"citizen_id": 3, "town": "Керчь", "street": "Иосифа Бродского", "building": "2", "apartment": 11,
             "name": "Романова Мария Леонидовна", "birth_date": "23.11.1986", "gender": "female", "relatives": []}
        ]}
        response = requests.post(url + "/imports", json=data)
        self.assertEqual(response.status_code, 201)
        import_id = response.json()['data']['import_id']

        data['data'] = deepcopy(data['citizens'])
        del data['citizens']

        data['data'][0]['relatives'] = [2, 3]
        data['data'][1]['relatives'] = [1]
        data['data'][2]['relatives'] = [1]

        upd = deepcopy(data['data'][0])
        del upd['citizen_id']
        response = requests.patch(url + f"/imports/{import_id}/citizens/1", json=upd)
        self.assertEqual(response.status_code, 200)
        upd = deepcopy(data['data'][0])
        self.assertDictEqual(upd, response.json()['data'])

        self.check_import(import_id, data)

    def test_n_patch_not_unique_rel_id(self):
        data = {"citizens": [
            {"citizen_id": 1, "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7,
             "name": "Иванов Иван Иванович", "birth_date": "26.12.1986", "gender": "male", "relatives": [2]},
            {"citizen_id": 2, "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7,
             "name": "Иванов Сергей Иванович", "birth_date": "17.04.1997", "gender": "male", "relatives": [1]},
            {"citizen_id": 3, "town": "Керчь", "street": "Иосифа Бродского", "building": "2", "apartment": 11,
             "name": "Романова Мария Леонидовна", "birth_date": "23.11.1986", "gender": "female", "relatives": []}
        ]}
        response = requests.post(url + "/imports", json=data)
        self.assertEqual(response.status_code, 201)
        import_id = response.json()['data']['import_id']

        data['data'] = deepcopy(data['citizens'])
        del data['citizens']

        data['data'][0]['relatives'] = [3, 3]

        upd = deepcopy(data['data'][0])
        del upd['citizen_id']
        response = requests.patch(url + f"/imports/{import_id}/citizens/1", json=upd)
        self.assertEqual(response.status_code, 400)

    def test_n_patch_empty(self):
        data = {"citizens": [
            {"citizen_id": 1, "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7,
             "name": "Иванов Иван Иванович", "birth_date": "26.12.1986", "gender": "male", "relatives": [2]},
            {"citizen_id": 2, "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7,
             "name": "Иванов Сергей Иванович", "birth_date": "17.04.1997", "gender": "male", "relatives": [1]},
            {"citizen_id": 3, "town": "Керчь", "street": "Иосифа Бродского", "building": "2", "apartment": 11,
             "name": "Романова Мария Леонидовна", "birth_date": "23.11.1986", "gender": "female", "relatives": []}
        ]}
        response = requests.post(url + "/imports", json=data)
        self.assertEqual(response.status_code, 201)
        import_id = response.json()['data']['import_id']

        response = requests.patch(url + f"/imports/{import_id}/citizens/1", json={})
        self.assertEqual(response.status_code, 400)

    def test_n_patch_invalid_cit_id(self):
        data = {"citizens": [
            {"citizen_id": 1, "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7,
             "name": "Иванов Иван Иванович", "birth_date": "26.12.1986", "gender": "male", "relatives": []}
        ]}
        response = requests.post(url + "/imports", json=data)
        self.assertEqual(response.status_code, 201)
        import_id = response.json()['data']['import_id']

        data['data'] = deepcopy(data['citizens'])
        del data['citizens']

        upd = deepcopy(data['data'][0])
        del upd['citizen_id']
        upd['name'] = 'kek'
        response = requests.patch(url + f"/imports/{import_id}/citizens/48", json=upd)
        self.assertEqual(response.status_code, 404)

        self.check_import(import_id, data)

    def test_n_patch_invalid_date(self):
        data = {"citizens": [
            {"citizen_id": 1, "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7,
             "name": "Иванов Иван Иванович", "birth_date": "26.12.1986", "gender": "male", "relatives": []}
        ]}
        response = requests.post(url + "/imports", json=data)
        self.assertEqual(response.status_code, 201)
        import_id = response.json()['data']['import_id']

        data['data'] = deepcopy(data['citizens'])
        del data['citizens']

        upd = deepcopy(data['data'][0])
        del upd['citizen_id']
        upd['birth_date'] = "29.02.2019"
        response = requests.patch(url + f"/imports/{import_id}/citizens/1", json=upd)
        self.assertEqual(response.status_code, 400)

        self.check_import(import_id, data)


if __name__ == '__main__':
    unittest.main()
