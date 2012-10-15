from haystack import indexes
from haystack import site
from moviepeopleapp.models import People


class PeopleIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    name_autocomplete = indexes.EdgeNgramField(model_attr='name')

    def get_model(self):
        return People

site.register(People, PeopleIndex)