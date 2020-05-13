from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.shortcuts import render, redirect
from django.conf import settings
import json

from operator import attrgetter
from itertools import groupby
from datetime import datetime
from random import randint
import re

path_data =settings.NEWS_JSON_PATH




class Data:
    def __init__(self, path=path_data):
        self.path = path
        self.data = []

    def changeTime(self, new):
        new.update({"created": datetime.fromisoformat(new["created"])})
        return new

    def load_data(self):
        with open(self.path, "r") as file:
            self.data = [self.changeTime(new) for new in json.load(file)]

    def get_new_by_id(self, id):
        if not self.data:
            self.load_data()
        new = list(filter(lambda item: int(item["link"]) == id, self.data))
        if new:
            return new[0]

    def get_all(self):
        if not self.data:
            self.load_data()
        return self.group_news(self.data)

    def get_by_title(self, text_search):
        pattern_search=re.compile(text_search,re.IGNORECASE)

        is_find = lambda text: pattern_search.search(text)
        news= [new for new in self.data if is_find(new["title"])]
        return self.group_news(news)


    def group_news(self,news):
        """
        return data group by date and sorted in reverse order
        """
        keyfunc = lambda item: item["created"].date()
        new_sorted = sorted(news, key=keyfunc, reverse=True)

        return [(d, list(sorted(items, key=lambda item: item["created"], reverse=True))) for d, items in
                groupby(new_sorted, key=keyfunc)]

    def getId(self):
        return list(map(lambda n: n["link"], self.data))

    def createId(self):
        id = 1
        while id in self.getId():
            id = randint(1, 5000)
        return id

    def create(self, title, text):
        """
        add a new {title,text,created } to data
        and save data to file
        """
        now = datetime.now()
        new = {"title": title, "text": text, "link": self.createId(), "created": now}
        self.save(new)
        return True

    def __new_to_string(self, new):
        """
        change type of created : datetime  to  string
        """
        cp = new.copy()
        cp.update({"created": new["created"].isoformat()})
        return cp

    def save(self, item):
        """
        transform item and save data to json file
        """
        with open(path_data, "w") as file:
            self.data.append(item)
            temp = list(map(self.__new_to_string, self.data))
            json.dump(temp, file)



data = Data()


def home(request):
    return redirect("/news/")


def main(request):
    text_search = request.GET.get("q")
    print("text_search",text_search)
    if text_search:
         news = data.get_by_title(text_search)
    else:
        news = data.get_all()


    return render(request, "news/news.html", context={"news": news})


class CreateNew(View):
    def get(self, request, *args, **kwargs):
        return render(request, "news/create.html")

    def post(self, request, *args, **kwargs):
        new = request.POST
        if new.get("title") and new.get("text"):
            data.create(new.get("title"), new.get("text"))

        return redirect("/news/")


class News(View):

    def get(self, request, id=0):

        new = data.get_new_by_id(id)
        if not new:
            return redirect("/news")
        else:
            return render(request, "news/show.html", context={"new": new})
