import asyncio
import aiohttp
import json
import os
import time
import re
from periodictable import formula
from .getCategory import getCategorys
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors
from .models import Substances, Store_exchange_json
from django.apps import apps
from .Store import Store


class Exchanger:
    Storer = Store()
    all_databases = apps.get_models()

    def generate(self, which_database):
        which_database = "Substances"
        data_for_file = []
        target_db = None
        for db in self.all_databases:
            if db.__name__ == which_database:
                target_db = db
                print(target_db)
                break
        if target_db is None:
            return False
        
        substances_in_db = target_db.objects.all()
        first_sub = target_db.objects.first()
        keys = first_sub.__dict__.keys()
        keys_to_remove = ['_state', 'id']
        usefull_keys = [key for key in keys if key not in keys_to_remove]
       
        print(usefull_keys)
        for sub in substances_in_db:
            sub_data = {}
            for key in usefull_keys:
                if key != "last_changed_at":
                    sub_data[key] = getattr(sub, key)
                else:
                     sub_data[key] = str(getattr(sub, key))
            data_for_file.append(sub_data)
        return data_for_file

    def process(self,file):
        self.Storer.Store_exchange_json(file)
        self.Storer.Substances(file)

        return True