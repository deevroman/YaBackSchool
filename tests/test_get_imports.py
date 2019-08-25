import unittest
import requests
from datetime import datetime
from copy import deepcopy

# url = "http://84.201.154.22:8080"
url = "http://localhost:8080"


class MyTestCase(unittest.TestCase):
    def test_n_get_imports_invalid_import_id(self):
        response = requests.get(url+"/imports/-1/citizens")
        self.assertEqual(response.status_code, 404)



if __name__ == '__main__':
    unittest.main()
