import yaml

class ApiKey:
    __type:str
    __key:str
    __name:str
    
    def __init__(self,name:str,type:str,key:str,**_kwargs:str) -> None:
        self.__type = type
        self.__key = key
        self.__name = name
    
    @property
    def type(self) -> str: 
        return self.__type
    
    @property
    def key(self) -> str:
        return self.__key
    
    @property
    def name(self) -> str:
        return self.__name
    
    def __str__(self) -> str:
        return f"{self.__name}: type={self.__type} key={self.__key}"
    
    
class ApiKeys:    
    __api_dict:dict[str,ApiKey]
    
    def __init__(self,file_path:str="api_keys.yaml") -> None:
        self.load(file_path)
    
    def load(self,file_path:str):
        self.__api_dict = {}
        with open(file_path,"r",encoding="utf-8") as api_keys_file:
            api_dict = yaml.load(api_keys_file.read(),yaml.FullLoader)
            for key,value in api_dict.items():
                self.__api_dict[key] = ApiKey(key,**value)
        
    def list_keys(self) -> dict[str,ApiKey]:
        return self.__api_dict.copy()
    
    def key_of(self,api_name:str) -> ApiKey:
        if api_name not in self.__api_dict.keys():
            raise KeyError(f"API Key Of {api_name} Not Found")
        return self.__api_dict[api_name]

