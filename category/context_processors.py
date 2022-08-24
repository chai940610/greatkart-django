#steps to create context processor
from .models import Category


def menu_links(request):
    #fetch all the category
    links=Category.objects.all()
    return dict(links=links)  