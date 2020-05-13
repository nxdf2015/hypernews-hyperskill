from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.shortcuts import render,redirect
from django.conf import settings
import json


path_data=settings.NEWS_JSON_PATH

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


data=Data()



def home(request):
    return HttpResponse("Coming soon")

def main(request):
    return render(request,"news/main.html")

class News(View):

    def get(self,request,id=0):

        new=data.get_new_by_id(id)
        if not new :
            return redirect("/news")
        else:
            return render(request,"news/show.html",context={"new":new,"id":id})
