import unittest
import requests
from datetime import datetime
import numpy as np
import random
from itertools import groupby
from operator import itemgetter


url = "http://localhost:8080"


class MyTestCase(unittest.TestCase):
    def check_import(self, import_id, data):
        response = requests.get(url + f"/imports/{import_id}/citizens")
        self.assertEqual(response.status_code, 200)
        for i in response.json()['data']:
            datetime.strptime(i['birth_date'], "%d.%m.%Y")
        self.assertDictEqual(data, response.json())

    def test_p_percentile(self):
        data = {"citizens": [
            {"citizen_id": i, "town": "Москва" + str(random.randint(0, 10)), "street": "Льва Толстого",
             "building": "16к7стр5", "apartment": 7,
             "name": "Иванов Иван Иванович", "birth_date": "20.08." + str(random.randint(1948, 2018)), "gender": "male",
             "relatives": []}
            for i in range(100)
        ]}

        response = requests.post(url + "/imports", json=data, timeout=10)
        self.assertEqual(response.status_code, 201)
        import_id = response.json()['data']['import_id']

        def get_age(today, d2):
            return (today.year - d2.year) - ((today.month, today.day) < (d2.month, d2.day))

        today = datetime.today()
        rows = [[i['town'], get_age(today, datetime.strptime(i['birth_date'], "%d.%m.%Y"))] for i in data['citizens']]
        rows.sort(key=itemgetter(0))
        result = []
        for elt, items in groupby(rows, itemgetter(0)):
            p50, p75, p99 = np.percentile(np.array([i[1] for i in items]), q=[50, 75, 99]).round(2).tolist()
            result.append({'town': elt, 'p50': p50, 'p75': p75, 'p99': p99})
        good = {
            'data': sorted(result, key=itemgetter('town'))
        }

        response = requests.get(url + f"/imports/{import_id}/towns/stat/percentile/age")
        self.assertEqual(response.status_code, 200)
        response = response.json()
        response['data'] = sorted(response['data'], key=itemgetter('town'))
        self.assertDictEqual(good, response)

    def test_n_percentile_invalid_import_id(self):
        response = requests.get(url + "/imports/-1/towns/stat/percentile/age")
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
