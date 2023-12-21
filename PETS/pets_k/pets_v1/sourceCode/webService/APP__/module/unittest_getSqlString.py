#!/usr/bin/python
# -*- coding: utf-8 -*-


from getSqlString import *
import unittest
from os import path, getcwd


class functionTestCase(unittest.TestCase):


    def test_getGenNumLevel(self):
        colInfo = {
            'colName':'money',
            'level':'1000',
            'apiName':'getGenNumLevel'
        }

        exceped =  'getGenNumLevel_(money, "1000") as money'
        print("test_getGenNumLevel exceped: ",exceped)
        self.assertEqual(exceped, getGenNumLevel(colInfo))



    def test_getGenDate(self):
        colInfo = {
            'colName':'date',
            'level':'Y',
            'apiName':'getGenDate'
        }

        exceped =  'getGenDate_(date, "Y") as date'
        print("test_getGenDate exceped: ",exceped)
        self.assertEqual(exceped, getGenDate(colInfo))



    def test_getGenString(self):
        colInfo = {
            'colName':'ip',
            'beginPoint':'0',
            'endPoint':'6',
            'apiName':'getGenString'
        }

        exceped =  'getGenString_(ip, "0", "6") as ip'
        print("test_getGenString exceped: ",exceped)
        self.assertEqual(exceped, getGenString(colInfo))

    def test_getGenSHA1(self):
        colInfo = {
            'colName':'id',
            'apiName':'getGenSHA1'
        }

        exceped =  'getGenSHA1_(id) as id'
        print("test_getGenSHA1 exceped: ",exceped)
        self.assertEqual(exceped, getGenSHA1(colInfo))


    def test_getGenNumInterval(self):
        colInfo = {
            'colName':'age',
            'valueStart':['1','11','21','31','41'],
            'valueEnd':['10','20','30','40','50'],
            'toValue': ['5','15','25','35','45'],
            'apiName':'getGenNumInterval'
        }

        exceped =  'getGenNumInterval_(age,array("1","11","21","31","41"),array("10","20","30","40","50"),array("5","15","25","35","45")) as age'
        print("test_getGenNumInterval exceped: ",exceped)
        self.assertEqual(exceped, getGenNumInterval(colInfo))


    def test_getGenUdf(self):
        fileName = path.join( getcwd(),"app","devp","module","country_rule.txt")
        colInfo = {
            'colName':'country',
            'apiName':'getGenUdf',
            'userRule':fileName,
            'level':'1'
        }

        exceped =  'getGenUdf_(country, "Spain:Europe;Singapore:Asia", "False", "others") as country'
        print("test_getGenUdf exceped: ",exceped)
        self.assertEqual(exceped, getGenUdf(colInfo))

    def test_getGenAddress(self):
        colInfo = {
            'colName':'address',
            'apiName':'getGenAddress',
            'level':'C'
        }

        exceped =  'getGenAddress_(address, "區") as address'
        print("test_getGenAddress exceped: ",exceped)
        self.assertEqual(exceped, getGenAddress(colInfo))


if __name__ == '__main__':
    unittest.main()


