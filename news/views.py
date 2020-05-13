from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.shortcuts import render,redirect
from django.conf import settings
import json

from operator import attrgetter
from itertools import groupby
from datetime import datetime
path_data=settings.NEWS_JSON_PATH

def get_date(d):
    """
    @arg  date_string   iso format
    return date object
    """
    return datetime.fromisoformat(d).date()

def get_datetime(d):
    return datetime.fromisoformat(d)

class Data:
    def __init__(self,path=path_data):
        self.path=path
        self.data=[]

    def load_data(self):
        with open(self.path,"r") as file:
            self.data=json.load(file)


    def get_new_by_id(self,id):
        if not self.data:
            self.load_data()
        new=list(filter(lambda item : int(item["link"])==id , self.data ))
        if new :
            return new[0]

    def get_all(self):
        if not self.data:
            self.load_data()
        keyfunc=lambda item : get_date(item["created"])
        new_sorted=sorted(self.data,key=keyfunc,reverse=True)

        return [(d,list(sorted(items,key=lambda item : get_datetime(item["created"]),reverse=True))  )for d,items in groupby(new_sorted, key=keyfunc)]



data=Data()



def home(request):
    return render(request,"news/index.html")

def main(request):
    news=data.get_all()
    return render(request,"news/news.html",context={"news":news})

class News(View):

    def get(self,request,id=0):

        new=data.get_new_by_id(id)
        if not new :
            return redirect("/news")
        else:
            return render(request,"news/show.html",context={ "new":new,"id":id})
