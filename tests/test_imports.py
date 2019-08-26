import unittest
import requests
from datetime import datetime
from copy import deepcopy
import random


url = "http://localhost:8080"


class MyTestCase(unittest.TestCase):
    def check_import(self, import_id, data):
        response = requests.get(url + f"/imports/{import_id}/citizens")
        self.assertEqual(response.status_code, 200)
        for i in response.json()['data']:
            datetime.strptime(i['birth_date'], "%d.%m.%Y")
        self.assertDictEqual(data, response.json())

    def test_p_imports_one_req(self):
        data = {"citizens": [
            {"citizen_id": 1, "town": "Moscow", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7,
             "name": "Иванов Иван Иванович", "birth_date": "26.12.1986", "gender": "male", "relatives": []}
        ]}
        response = requests.post(url + "/imports", json=data)
        self.assertEqual(response.status_code, 201)

        data['data'] = deepcopy(data['citizens'])
        del data['citizens']

        import_id = response.json()['data']['import_id']
        response = requests.get(url + f"/imports/{import_id}/citizens")
        self.assertEqual(response.status_code, 200)
        for i in response.json()['data']:
            datetime.strptime(i['birth_date'], "%d.%m.%Y")
        self.assertDictEqual(response.json(), data)

    def test_p_imports_big_test(self):
        data = {"citizens": [
            {"citizen_id": i, "town": "Москва" + str(random.randint(0, 10)), "street": "Льва Толстого",
             "building": "16к7стр5", "apartment": 7,
             "name": "Иванов Иван Иванович", "birth_date": "20.08." + str(random.randint(1948, 2018)), "gender": "male",
             "relatives": []}
            for i in range(10000)
        ]}
        response = requests.post(url + "/imports", json=data, timeout=10)
        self.assertEqual(response.status_code, 201)

    def test_p_imports_jo(self):
        data = {"citizens": [
            {"citizen_id": 1, "town": "ё", "street": "ё", "building": "16ё7ёёё5", "apartment": 7,
             "name": "ё ё ё", "birth_date": "26.12.1986", "gender": "male", "relatives": []}
        ]}
        response = requests.post(url + "/imports", json=data)
        self.assertEqual(response.status_code, 201)

    def test_p_imports_many(self):
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

    def test_n_import_not_unique_cit_id(self):
        data = {"citizens": [
            {"citizen_id": 1, "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7,
             "name": "Иванов Иван Иванович", "birth_date": "26.12.1986", "gender": "male", "relatives": [2]},
            {"citizen_id": 1, "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7,
             "name": "Иванов Сергей Иванович", "birth_date": "17.04.1997", "gender": "male", "relatives": [1]},
        ]}
        response = requests.post(url + "/imports", json=data)
        self.assertEqual(response.status_code, 400)

    def test_n_import_cit_id_negative(self):
        data = {"citizens": [
            {"citizen_id": -48, "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7,
             "name": "Иванов Иван Иванович", "birth_date": "26.12.1986", "gender": "male", "relatives": [2]},
        ]}
        response = requests.post(url + "/imports", json=data)
        self.assertEqual(response.status_code, 400)

    def test_n_import_rel_not_in_import(self):
        data = {"citizens": [
            {"citizen_id": 1, "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7,
             "name": "Иванов Иван Иванович", "birth_date": "26.12.1986", "gender": "male", "relatives": [2]},
        ]}
        response = requests.post(url + "/imports", json=data)
        self.assertEqual(response.status_code, 400)

    def test_n_import_rel_not_reversive(self):
        data = {"citizens": [
            {"citizen_id": 1, "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7,
             "name": "Иванов Иван Иванович", "birth_date": "26.12.1986", "gender": "male", "relatives": [2]},
            {"citizen_id": 2, "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7,
             "name": "Иванов Иван Иванович", "birth_date": "26.12.1986", "gender": "male", "relatives": []},
        ]}
        response = requests.post(url + "/imports", json=data)
        self.assertEqual(response.status_code, 400)

    def test_n_import_date_more_today(self):
        data = {"citizens": [
            {"citizen_id": 1, "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7,
             "name": "Иванов Иван Иванович", "birth_date": "26.12.2986", "gender": "male", "relatives": []},
        ]}
        response = requests.post(url + "/imports", json=data)
        self.assertEqual(response.status_code, 400)

    def test_n_import_date_invalid_month(self):
        data = {"citizens": [
            {"citizen_id": 1, "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7,
             "name": "Иванов Иван Иванович", "birth_date": "26.13.1986", "gender": "male", "relatives": []},
        ]}
        response = requests.post(url + "/imports", json=data)
        self.assertEqual(response.status_code, 400)

    def test_n_imports_invalid_field_citizens_1(self):
        data = {"citizens": {}}
        response = requests.post(url + "/imports", json=data)
        self.assertEqual(response.status_code, 400)

    def test_n_imports_invalid_field_citizens_2(self):
        data = {"citizen": {}}
        response = requests.post(url + "/imports", json=data)
        self.assertEqual(response.status_code, 400)

    def test_n_imports_invalid_field_not_field(self):
        data = {"citizens": [
            {"citizen_id": 1, "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7,
             "name": "Иванов Иван Иванович", "birth_date": "26.12.1986", "gender": "male", "relatives": [2]}
        ]}

        for i in data['citizens'][0]:
            tmp = deepcopy(data)
            del tmp['citizens'][0][i]
            response = requests.post(url + "/imports", json=tmp)
            self.assertEqual(response.status_code, 400)

    def test_n_imports_invalid_gender(self):
        data = {"citizens": [
            {"citizen_id": 1, "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7,
             "name": "Иванов Иван Иванович", "birth_date": "26.12.1986", "gender": "not_male", "relatives": []}
        ]}
        response = requests.post(url + "/imports", json=data)
        self.assertEqual(response.status_code, 400)

    def test_n_imports_invalid_field_rel(self):
        data = {"citizens": [
            {"citizen_id": 1, "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7,
             "name": "Иванов Иван Иванович", "birth_date": "26.12.1986", "gender": "male", "relatives": {}}
        ]}
        response = requests.post(url + "/imports", json=data)
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
