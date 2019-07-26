#import conf.bootstrap as config
#import conf.datakey as datakey
from .hashicorp_base import ConnBase
import hvac
import os
import json

class VaultCon(ConnBase):
    """Class to construct the dict properties for the app from Consul and Vault
    """

    exception_key = ['path_consul']
    exception_dict = {}

    def __init__(self):
        """Constructor inisiating all properties
        """
        vault_params = {}
        
        # construct the consul and vault params
        vault_params = self.get_configs_dict(config.vault)

        # construct the vault url
        vault_params['url'] = self.exception_dict['scheme_vault'] +'://' + self.exception_dict['host_vault'] + ':' + str(self.exception_dict['port_vault'])

        # construct the vault client objects
        self.vault = hvac.Client(**vault_params)
        self.vault.kv.default_kv_version = '1'

        # get the secret information from vault then save in self.secret dict
        self.secrets = self.vault.kv.read_secret(self.exception_dict['path_vault'])['data']
   

    def __construct_data_vault(self, data, key = ''):
        """construct secret configuration informations of the services from vault return config dict

        Keyword arguments:
        data -- the dict information that came from configuration.py for vault_app_configs
        key -- the string of the path that will be concated with sub key in data dict (default '')
        info -- the informations of the structures of the app configurations that will be merged with secret info (default {})
        """

        for k, v in data.items():
            if type(v) == dict:
                # recursive if the value of the item is dict
                info[k] = self.__construct_data_vault(v,key + '.' +k if key != '' else k, info[k] if k in info else {})
            else:
                # assign info dict with secret info with index k
                info[k] = self.secrets[key + '.' + k]

        return info

    def get_secret_kv(self):
        """run config constructor return dict all configs
        """ 
        return self.__construct_data_vault(data = datakey.vault_app_configs)