# osu_importer/objects/base_creator.py

import abc
from osu_importer.utils.utils import timeit, tag_imported

class BaseHitObjectCreator(abc.ABC):
    def __init__(self, hitobject, global_index, collection, config, data_manager, import_type):
        self.hitobject = hitobject
        self.global_index = global_index
        self.collection = collection
        self.config = config
        self.data_manager = data_manager
        self.import_type = import_type

    def create(self):
        with timeit(f"Create {self.__class__.__name__} {self.global_index:03d}_{getattr(self.hitobject, 'time', 'none')}"):
            obj = self.create_object()
            if obj is None:
                return None
            self.link_object_to_collection(obj)
            self.animate_object(obj)
            return obj

    @abc.abstractmethod
    def create_object(self):
        pass

    def animate_object(self, obj):
        pass

    def link_object_to_collection(self, obj):
        if self.collection:
            self.collection.objects.link(obj)
            if obj.users_collection:
                for col in obj.users_collection:
                    if col != self.collection:
                        col.objects.unlink(obj)
        tag_imported(obj)
