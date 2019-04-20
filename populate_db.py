import pandas as pd
import xlrd
from articles.models import *
from articles.serializers import *
import datetime

file = 'cardDB.xlsx'

wb = xlrd.open_workbook(file)
sheet = wb.sheet_by_index(0)

# for testing
# for i in range(sheet.nrows-93):
#     print(sheet.row_values(i))

class excelConverter():
    def __init__(self, filename="cardDB.xlsx"):
        self.file = filename
        self.wb = xlrd.open_workbook(self.file)
        self.priSheet = self.wb.sheet_by_index(0)
    def print_cells(self):
        for i in self.priSheet.get_rows():
            print(i[0])
    def print_articles(self):
        print(Article.objects.all())
    def convert_list_to_dict(self, row_as_list):
        '''
        row_values(0) is the first row defining field name --> change if required
        '''
        dict = {}
        titles = sheet.row_values(0)
        for i in range(len(row_as_list)):
            dict[titles[i]] = row_as_list[i]
        return dict
    def serialize_excel_row(self, row_as_dict, desired_pk_value=None):
        headline = row_as_dict['headline']
        if Article.objects.filter(headline=row_as_dict['headline']).exists():
            anot = Article.objects.get(headline=headline)
            print("Article already exists {}".format(anot))
        else:
            if desired_pk_value == None:
                a=Article.objects.create()
            else:
                a = Article.objects.create(pk=desired_pk_value)
            # for k,v in row_as_dict.items():
            #     if v == "":
            #         row_as_dict[k] = None
            if (Tag.objects.filter(name=row_as_dict['tag']).exists()):
                t = Tag.objects.get(name=row_as_dict['tag'])
            else:
                t = Tag.objects.create(name=row_as_dict['tag'])
            #TODO
            # for title in row_as_dict.keys():
            a.headline = row_as_dict['headline']
            a.tag = t
            if row_as_dict["truthvalue"] == None or row_as_dict["truthvalue"] == False or row_as_dict["truthvalue"] == True:
                a.truth_value = row_as_dict["truthvalue"]
            elif row_as_dict["truthvalue"] == 0:
                a.truth_value = False
            elif row_as_dict["truthvalue"] == 1:
                a.truth_value = True
            else:
                a.truth_value = None
                print("Something wrong with Article {} TRUTH_VALUE".format(a.pk))

            a.rating = row_as_dict['rating']
            a.domain = row_as_dict['domain']
            a.url = row_as_dict['website']
            a.summary = row_as_dict['summary']
            if row_as_dict['author'] == None:
                a.author = ""
            else:
                a.author = row_as_dict['author']
            print(row_as_dict['date'])
            print(type(row_as_dict['date']))

            dt = datetime.datetime(*xlrd.xldate_as_tuple(row_as_dict['date'],self.wb.datemode))
            a.published=dt
            a.save()
            print(a)
    def bulk_serialize(self):
        for i in range(1, self.priSheet.nrows-1):
            row_value = self.priSheet.row_values(i)
            dict = self.convert_list_to_dict(row_value)
            self.serialize_excel_row(dict,i+1)

# ec1 = excelConverter("cardDB.xlsx")
# dict = ec1.convert_list_to_dict(sheet.row_values(2))
# print(dict['headline'])
# print(dict['tag'])
