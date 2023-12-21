

import unittest
from auto_upload import *
from MyLib.connect_sql import ConnectSQL


class TestFlaskApiUsingRequests(unittest.TestCase):

    def test_checkUserList(self):
        conn = ConnectSQL()
        userListResult1 = checkUserList(conn, "deidadmin")
        self.assertEqual(userListResult1['result'], True)

    def test_scanFiles(self):
        scanResult = scanFiles("/root/data/input", unittest)
        self.assertEqual(scanResult["unittest"]["project1"]["isFile"], True)
        self.assertEqual(scanResult["unittest"]["project1"]["csvFiles"], ["file1.csv"])
        self.assertEqual(scanResult["unittest"]["project1"]["otherFiles"], ["file2.txt"])




if __name__ == "__main__":
    unittest.main()
