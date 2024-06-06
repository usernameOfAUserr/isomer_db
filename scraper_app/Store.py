import datetime
from .models import Substances, Store_exchange_json

class Store():
     def Substances(self, list_of_substances):
        for substance in list_of_substances:
            try:
                data_dict = substance
                existing_object = Substances.objects.filter(source=substance["source"]).first()
                if existing_object:
                    existing_object.delete()
                Substances.objects.create(
                    smiles=data_dict['smiles'],
                    names=data_dict['names'],
                    iupac_names=data_dict['iupac_names'],
                    formula=data_dict['formula'],
                    inchi=data_dict['inchi'],
                    inchi_key=data_dict['inchi_key'],
                    molecular_mass=data_dict['molecular_mass'],
                    cas_num=data_dict['cas_num'],
                    categories=data_dict['categories'],
                    source=data_dict["source"],
                    validated=data_dict['validated'],
                    deleted=data_dict['deleted'],
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