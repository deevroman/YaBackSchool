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

    def test_p_birthdays_with_patch(self):
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

        response = requests.get(url+f"/imports/{import_id}/citizens/birthdays")
        self.assertEqual(response.status_code, 200)
        good = {"data": {str(i): [] for i in range(1, 12+1)}}
        good['data']['4'] = [{'citizen_id': 1, "presents": 1}]
        good['data']['12'] = [{'citizen_id': 2, "presents": 1}]
        self.assertDictEqual(good, response.json())

        data['data'][0]['birth_date'] = "11.01.1999"

        upd = deepcopy(data['data'][0])
        del upd['citizen_id']
        response = requests.patch(url + f"/imports/{import_id}/citizens/1", json=upd)
        self.assertEqual(response.status_code, 200)
        upd = deepcopy(data['data'][0])
        self.assertDictEqual(upd, response.json()['data'])
        self.check_import(import_id, data)

        response = requests.get(url+f"/imports/{import_id}/citizens/birthdays")
        self.assertEqual(response.status_code, 200)
        good = {"data": {str(i): [] for i in range(1, 12+1)}}
        good['data']['4'] = [{'citizen_id': 1, "presents": 1}]
        good['data']['1'] = [{'citizen_id': 2, "presents": 1}]
        self.assertDictEqual(good, response.json())

    def test_n_birthdays_invalid_import_id(self):
        response = requests.get(url+"/imports/-1/citizens/birthdays")
        self.assertEqual(response.status_code, 404)



if __name__ == '__main__':
    unittest.main()
