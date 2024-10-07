import pandas as pd
import geopandas as gpd
from sqlalchemy import text

from .geolevel import Geolevel
from .network import Network

class DistancierSession:
    # Constructor
    def __init__(
            self,
            session_id:int,
            name:str,
            engine:str,
            network_id_start:int,
            network_id_end:int,
            geolevel_id_start:int,
            geolevel_id_end:int,
            direction:str,
            max_distance:int,
            max_time:int,
            max_calc_out:int,
            no_route:bool,
            org:'Org' # type: ignore
    ):
        self._session_id = session_id
        self._name = name
        self._engine = engine
        try:
            self._network_id_start = int(network_id_start)
        except: 
            self._network_id_start = None
        try:
            self._network_id_end = int(network_id_end)
        except:
            self._network_id_end = None
        try:
            self._geolevel_id_start = int(geolevel_id_start)
        except:
            self._geolevel_id_start = None
        try:
            self._geolevel_id_end = int(geolevel_id_end)
        except:
            self._geolevel_id_end = None
        self._direction = direction
        try:
            self._max_distance = int(max_distance)
        except:
            self._max_distance = None
        try:
            self._max_time = int(max_time)
        except:
            self._max_time = None
        try:
            self._max_calc_out = int(max_calc_out)
        except:
            self._max_calc_out = None
        self._no_route = no_route
        self._org = org

    # Getters and setters
    @property
    def session_id(self): return self._session_id
    @property
    def name(self): return self._name
    @property
    def engine(self): return self._engine
    @property
    def network_id_start(self): return self._network_id_start
    @property
    def network_id_end(self): return self._network_id_end
    @property
    def geolevel_id_start(self): return self._geolevel_id_start
    @property
    def geolevel_id_end(self): return self._geolevel_id_end
    @property
    def direction(self): return self._direction
    @property
    def max_distance(self): return self._max_distance
    @property
    def max_time(self): return self._max_time
    @property
    def max_calc_out(self): return self._max_calc_out
    @property
    def no_route(self): return self._no_route
    @property
    def org(self): return self._org

    # Magic Method
    def __str__(self) -> str:
        return f"DistancierSession({self._session_id} - {self._name})"
    
    # Public Methods
    def getStartingType(self)->str:
        if self._network_id_start:
            return 'network'
        else:
            return 'geolevel'
    def getEndingType(self)->str:
        if self._network_id_end:
            return 'network'
        else:
            return 'geolevel'
    def getStartingObject(self)->Network|Geolevel:
        if self._network_id_start:
            return self._org.getNetwork(self._network_id_start)
        else:
            return self._org.getGeolevel(self._geolevel_id_start)
        
    def getEndingObject(self)->Network|Geolevel:
        if self._network_id_end:
            return self._org.getNetwork(self._network_id_end)
        else:
            return self._org.getGeolevel(self._geolevel_id_end)
        
    def getDistancier(self)->pd.DataFrame:
        # Query
        q = f"SELECT * FROM ggo_distancier WHERE session_id = {self._session_id}"
        # Df
        return self._org.query_df(q)
    
    def to_json(self):
        return {
            "session_id": self._session_id,
            "name": self.name,
            "engine": self._engine,
            "network_id_start": self._network_id_start,
            "network_id_end": self._network_id_end,
            "geolevel_id_start": self._geolevel_id_start,
            "geolevel_id_end": self._geolevel_id_end,
            "direction": self._direction,
            "max_distance": self._max_distance,
            "max_time": self._max_time,
            "max_calc_out": self._max_calc_out,
            "no_route": self._no_route
        }
    
    def getPoisIdList(self)->list:
        pois_ids_list = []
        if self.getStartingType() == 'network':
            q = f"SELECT DISTINCT poi_id_start FROM ggo_distancier WHERE session_id = {self._session_id} AND poi_id_start IS NOT NULL"
            df = self._org.query_df(q)
            pois_ids_list += df['poi_id_start'].tolist()
        if self.getEndingType() == 'network':
            q = f"SELECT DISTINCT poi_id_end FROM ggo_distancier WHERE session_id = {self._session_id} AND poi_id_end IS NOT NULL"
            df = self._org.query_df(q)
            pois_ids_list += df['poi_id_end'].tolist()
        return pois_ids_list
    
    def getGeounitCodeList(self)->list:
        geounit_code_list = []
        if self.getEndingType() == 'geolevel':
            q = f"SELECT DISTINCT geounit_code_start FROM ggo_distancier WHERE session_id = {self._session_id} AND geounit_code_start IS NOT NULL"
            df = self._org.query_df(q)
            geounit_code_list += df['geounit_code_start'].tolist()
        if self.getEndingType() == 'geolevel':
            q = f"SELECT DISTINCT geounit_code_end FROM ggo_distancier WHERE session_id = {self._session_id} AND geounit_code_end IS NOT NULL"
            df = self._org.query_df(q)
            geounit_code_list += df['geounit_code_end'].tolist()
        return geounit_code_list