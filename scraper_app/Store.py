import datetime
from .models import Substances, Store_exchange_json

class Store():
     def Substances(self, list_of_substances):
        for substance in list_of_substances:
            try:
                data_dict = substance
                url = substance['source_url']
                source_name = substance['source_name']
                existing_object = Substances.objects.filter(source_name=source_name, source_url=url).first()
                if existing_object:
                    existing_object.delete()
                Substances.objects.create(
                    smiles=data_dict['smiles'],
                    names=data_dict['names'],
                    iupac_name=data_dict['iupac_name'],
                    formular=data_dict['formular'],
                    inchi=data_dict['inchi'],
                    inchi_key=data_dict['inchi_key'],
                    molecular_mass=data_dict['molecular_mass'],
                    cas_num=data_dict['cas_num'],
                    category=data_dict['category'],
                    source_name=data_dict['source_name'],
                    source_url=data_dict['source_url'],
                    valid=data_dict['valid'],
                    deleted=data_dict['deleted'],
                    version=data_dict['version'],
                    details=data_dict['details']
                )
            except:
                print(str(substance)+ " couldnt be stored")

                
     def  Store_exchange_json(self, one_file):
        file_name = str(one_file)
        name = str(file_name) + str(datetime.datetime.now().time())
        Store_exchange_json.objects.create(
            name = name,
            file=one_file
        )