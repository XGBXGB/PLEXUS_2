import geojson
from geojson import Feature, Polygon, FeatureCollection
import json
import io
import sys
from area import area
import shapely
from shapely.geometry import shape, Point
import pygeoj
import math
import pandas as pd
# from models.taz import TAZ

class landuseObj:
    def __init__(self, name, area):
        self.name = name
        self.area = area

class TAZ:
    def __init__(self):
        self.zone_feature = None
        self.zone_polygon = None
        self.centroid = None
        self.trips = 0
        self.trips_produced = 0
        self.trips_attracted = 0
        self.main_landuse = ""
        self.no_hh = 0
        self.no_mem = 0
        self.no_mem_educwork = 0
        self.total_income = 0
        self.total_amenities = 0
        self.no_amty_sustenance = 0
        self.no_amty_education = 0
        self.no_amty_transport = 0
        self.no_amty_healthcare = 0
        self.no_amty_finance = 0
        self.no_amty_commerce = 0
        self.no_amty_entertainment = 0
        self.no_amty_other = 0
        self.lu_ind_commercial = 0
        self.lu_ind_parks = 0
        self.lu_ind_industrial = 0
        self.lu_ind_agriculture = 0
        self.lu_ind_residential = 0
        self.lu_ind_utilities = 0

        self.lu_commercial_obj = landuseObj("commercial", 0)
        self.lu_parks_obj = landuseObj("parks", 0)
        self.lu_industrial_obj = landuseObj("industrial", 0)
        self.lu_agriculture_obj = landuseObj("agriculture", 0)
        self.lu_residential_obj = landuseObj("residential", 0)
        self.lu_utilities_obj = landuseObj("utilities", 0)
        self.lu_other_obj = landuseObj("other", 0)

    # def as_json(self):
    #     return dict(
    #         input_id=self.id, input_user=self.input_user,
    #         input_title=self.input_title,
    #         input_date=self.input_date.isoformat(),
    #         input_link=self.input_link)

    def __str__(self):
        return "no_hh:"+str(self.no_hh)+" no_mem:"+str(self.no_mem)+" total_income:"+str(self.total_income)

    def compute_landuse(self):
        landuse_list = [self.lu_commercial_obj, self.lu_parks_obj,self.lu_industrial_obj,
                        self.lu_agriculture_obj,self.lu_residential_obj,self.lu_utilities_obj,
                        self.lu_other_obj]

        best_landuse = landuse_list[0]
        for landuse in landuse_list:
            if(best_landuse.area < landuse.area):
                best_landuse = landuse

        self.main_landuse = best_landuse.name


    def get_attr_vals(self):
        if(self.no_hh>0):
            self.total_income = self.total_income/self.no_hh
        return [self.trips, self.no_hh, self.no_mem, self.no_mem_educwork, self.total_income,
                self.no_amty_sustenance, self.no_amty_education, self.no_amty_transport, self.no_amty_healthcare,
                self.no_amty_finance, self.no_amty_commerce, self.no_amty_entertainment, self.no_amty_other,
                self.lu_ind_commercial, self.lu_ind_parks, self.lu_ind_industrial, self.lu_ind_agriculture,
                self.lu_ind_residential, self.lu_ind_utilities]

    def get_attr_vals2(self):
        if(self.no_hh>0):
            self.total_income = self.total_income/self.no_hh/12
        return [self.trips, self.no_hh, self.no_mem, self.no_mem_educwork, self.total_income,
                self.no_amty_sustenance, self.no_amty_education, self.no_amty_transport, self.no_amty_healthcare,
                self.no_amty_finance, self.no_amty_commerce, self.no_amty_entertainment, self.no_amty_other,
                self.lu_commercial_obj.area, self.lu_parks_obj.area, self.lu_industrial_obj.area,
                self.lu_agriculture_obj.area, self.lu_residential_obj.area, self.lu_utilities_obj.area,
                self.lu_other_obj.area]

class TripAnalyzer:
    def __init__(self, taz_geo_files, cbms_files, amenity_files, landuse_files):
        self.traffic_analysis_zones = []
        self.taz_geo_files = taz_geo_files
        self.cbms_files = cbms_files
        self.amenity_files = amenity_files
        self.landuse_files = landuse_files


    def trip_analyze(self):
        wakoko = 0
        center_coors = []
        for file in self.taz_geo_files:
            geofile = pygeoj.load("media/trafficzones/"+str(file))
            ctr = 0
            for feature in geofile:
                print(str(ctr)+".) Zone Name: "+str(str(feature.properties['NAME_2']).encode(sys.stdout.encoding, errors='replace')))
                polygon = shape(feature.geometry)
                if(feature.geometry.type == "MultiPolygon"):
                    allparts = [p.buffer(0) for p in polygon]
                    feature.geometry = shapely.ops.cascaded_union(allparts)
                if(polygon.is_valid == False):
                    polygon = polygon.buffer(0)
                print("is valid? = " + str(polygon.is_valid))
                #print("orig area:"+str(polygon.area*11985.061579199087642730909628381)+" 2area: "+str(area({'type':feature.geometry.type,'coordinates':feature.geometry.coordinates})/1000000))
                raw_taz = TAZ()
                raw_taz.centroid = geojson.dumps(shapely.geometry.geo.shape(feature.geometry).centroid)
                center_coors.append(shapely.geometry.geo.shape(feature.geometry).centroid)
                print("Lat: "+str(shapely.geometry.geo.shape(feature.geometry).centroid.y)+" Long: "+str(str(shapely.geometry.geo.shape(feature.geometry).centroid.x)))
                #print("dumpcentroid: "+str(raw_taz.centroid))

                raw_taz.zone_feature = geojson.dumps(feature)
                raw_taz.zone_polygon = polygon
                self.traffic_analysis_zones.append(raw_taz)
                ctr += 1

        for index, coor in enumerate(center_coors):
            min = -1
            zone_index = -1
            for jndex, coor2 in enumerate(center_coors):
                #print("zC:"+str(zone.centroid))
                #print("zC1:" + str(zone.centroid[0]))
                #print("zC2:" + str(zone.centroid[1]))
                temp = abs((float(coor.x) - float(coor2.x))) + abs((float(coor.y) - float(coor2.y)))
                if(index!=jndex):
                    if(min == -1):
                        min = temp
                        zone_index = jndex
                    else:
                        if(temp<min):
                            min = temp
                            zone_index = jndex
            print("Nearest to Zone"+str(index+1)+" = Zone"+str(zone_index+1)+" distance:"+str(min))

        #Loop through all cbms files pa
        abandoned_ctr = 0
        for file in self.cbms_files:
            with open("media/households/"+str(file), encoding="utf-8") as json_data:
                json_elems = json.load(json_data)
                for json_obj in json_elems:
                    hh_lat, hh_long = json_obj['latitude'], json_obj['longitude']
                    if not(hh_lat == "0" and hh_long == "0"):
                        point = Point(float(hh_long),float(hh_lat))
                        falinany = 0
                        for index, zone in enumerate(self.traffic_analysis_zones):
                            if zone.zone_polygon.contains(point):
                                zone.no_hh = zone.no_hh + 1
                                zone.no_mem = zone.no_mem + int(json_obj['phsize'])
                                zone.no_mem_educwork = zone.no_mem_educwork + int(json_obj['toteduc'])+ int(json_obj['totjob'])
                                zone.total_income = zone.total_income + float(json_obj['totin'])
                                #print("zone.total_income = "+str(zone.total_income))
                                falinany = 1
                        if(falinany == 0):
                            abandoned_ctr = abandoned_ctr+1
                            #print("LAT:"+str(hh_lat)+" LONG:"+str(hh_long))
            print("wew")
        print("DID NOT FALL IN ANY XXXXX: "+str(abandoned_ctr))




        #Populate Amenity attributes
        for file in self.amenity_files:
            #geofile = pygeoj.load("media/amenities/" + str(file), encoding="utf8")
            with open("media/amenities/"+str(file), encoding="utf-8") as json_data:
                json_elems = json.load(json_data)
            #for feature in geofile:
            for json_obj in json_elems['features']:
                am_lat, am_long = json_obj['geometry']['coordinates'][0], json_obj['geometry']['coordinates'][1]
                #am_lat, am_long = feature.geometry.coordinates[0], feature.geometry.coordinates[0]
                if am_lat == "0" and am_long == "0":
                    print(line)
                else:
                    point = Point(float(am_lat), float(am_long))
                    for index, zone in enumerate(self.traffic_analysis_zones):
                        #print("LOOP PA MORE: "+str(zone.zone_polygon.contains(point))+" LAT,LONG:"+str(am_lat)+","+str(am_long))
                        if zone.zone_polygon.contains(point):
                            zone.total_amenities = zone.total_amenities + 1
                            amenity_type = json_obj['properties']['amenity_type']
                            #amenity_type = feature.properties.amenity_type
                            if amenity_type == "sustenance":
                                zone.no_amty_sustenance = zone.no_amty_sustenance + 1
                            elif amenity_type == "education":
                                zone.no_amty_education = zone.no_amty_education + 1
                            elif amenity_type == "transport":
                                zone.no_amty_transport = zone.no_amty_transport + 1
                            elif amenity_type == "healthcare":
                                zone.no_amty_healthcare = zone.no_amty_healthcare + 1
                            elif amenity_type == "finance":
                                zone.no_amty_finance = zone.no_amty_finance + 1
                            elif amenity_type == "commerce":
                                zone.no_amty_commerce = zone.no_amty_commerce + 1
                            elif amenity_type == "entertainment":
                                zone.no_amty_entertainment = zone.no_amty_entertainment + 1
                            elif amenity_type == "other":
                                zone.no_amty_other = zone.no_amty_other + 1

        for index, zone in enumerate(self.traffic_analysis_zones):
            print("#"+str(index))
            print("sustenance: "+str(zone.no_amty_sustenance))
            print("education: "+str(zone.no_amty_education))
            print("transport: "+str(zone.no_amty_transport))
            print("healthcare: "+str(zone.no_amty_healthcare))
            print("finance: "+str(zone.no_amty_finance))
            print("commerce: "+str(zone.no_amty_commerce))
            print("entertainment: "+str(zone.no_amty_entertainment))
            print("other: "+str(zone.no_amty_other))


        for file in self.landuse_files:
            with open("media/landuses/" + str(file), encoding="utf-8") as json_data:
                json_elems = json.load(json_data)
            for json_obj in json_elems['features']:
                for zone in self.traffic_analysis_zones:
                    if(json_obj['properties']['landuse_type'] == "commercial"):
                        zone.lu_commercial_obj.area = zone.lu_commercial_obj.area + (shape(json_obj['geometry']).intersection(zone.zone_polygon).area)
                    elif(json_obj['properties']['landuse_type'] == "parks"):
                        zone.lu_parks_obj.area = zone.lu_parks_obj.area + shape(json_obj['geometry']).intersection(zone.zone_polygon).area
                    elif(json_obj['properties']['landuse_type'] == "industrial"):
                        zone.lu_industrial_obj.area = zone.lu_industrial_obj.area + shape(json_obj['geometry']).intersection(zone.zone_polygon).area
                    elif(json_obj['properties']['landuse_type'] == "agriculture"):
                        zone.lu_agriculture_obj.area = zone.lu_agriculture_obj.area + shape(json_obj['geometry']).intersection(zone.zone_polygon).area
                    elif(json_obj['properties']['landuse_type'] == "residential"):
                        zone.lu_residential_obj.area = zone.lu_residential_obj.area + shape(json_obj['geometry']).intersection(zone.zone_polygon).area
                    elif(json_obj['properties']['landuse_type'] == "utilities"):
                        zone.lu_utilities_obj.area = zone.lu_utilities_obj.area + shape(json_obj['geometry']).intersection(zone.zone_polygon).area
                    elif(json_obj['properties']['landuse_type'] == "other"):
                        zone.lu_other_obj.area = zone.lu_other_obj.area + shape(json_obj['geometry']).intersection(zone.zone_polygon).area
            for zone in self.traffic_analysis_zones:
                zone.lu_commercial_obj.area = zone.lu_commercial_obj.area*11985.061579199087642730909628381 * 100
                zone.lu_parks_obj.area = zone.lu_parks_obj.area * 11985.061579199087642730909628381 * 100
                zone.lu_industrial_obj.area = zone.lu_industrial_obj.area * 11985.061579199087642730909628381 * 100
                zone.lu_agriculture_obj.area = zone.lu_agriculture_obj.area * 11985.061579199087642730909628381 * 100
                zone.lu_residential_obj.area = zone.lu_residential_obj.area * 11985.061579199087642730909628381 * 100
                zone.lu_utilities_obj.area = zone.lu_utilities_obj.area * 11985.061579199087642730909628381 * 100
                zone.lu_other_obj.area = zone.lu_other_obj.area * 11985.061579199087642730909628381 * 100



        for zone in self.traffic_analysis_zones:
            zone.compute_landuse()
            if (zone.main_landuse == "commercial"):
                print("went1")
                zone.lu_ind_commercial = 1
            elif (zone.main_landuse == "parks"):
                print("went2")
                zone.lu_ind_parks = 1
            elif (zone.main_landuse == "industrial"):
                print("went3")
                zone.lu_ind_industrial = 1
            elif (zone.main_landuse == "agriculture"):
                print("went4")
                zone.lu_ind_agriculture = 1
            elif (zone.main_landuse == "residential"):
                print("went5")
                zone.lu_ind_residential = 1
            elif (zone.main_landuse == "utilities"):
                print("went6")
                zone.lu_ind_utilities = 1

        # for index, landuse in enumerate(self.zone_landuse_setting):
        #     if(landuse == "commercial"):
        #         self.traffic_analysis_zones[index].main_landuse = "commercial"
        #         self.traffic_analysis_zones[index].lu_ind_commercial = 1
        #     elif(landuse == "parks"):
        #         self.traffic_analysis_zones[index].main_landuse = "parks"
        #         self.traffic_analysis_zones[index].lu_ind_parks = 1
        #     elif(landuse == "industrial"):
        #         self.traffic_analysis_zones[index].main_landuse = "industrial"
        #         self.traffic_analysis_zones[index].lu_ind_industrial = 1
        #     elif(landuse == "agriculture"):
        #         self.traffic_analysis_zones[index].main_landuse = "agriculture"
        #         self.traffic_analysis_zones[index].lu_ind_agriculture = 1
        #     elif(landuse == "residential"):
        #         self.traffic_analysis_zones[index].main_landuse = "residential"
        #         self.traffic_analysis_zones[index].lu_ind_residential = 1
        #     elif(landuse == "utilities"):
        #         self.traffic_analysis_zones[index].main_landuse = "utilities"
        #         self.traffic_analysis_zones[index].lu_ind_utilities = 1
        #     else:
        #         self.traffic_analysis_zones[index].main_landuse = "other"

        cols = ['trips','no_hh','no_mem','no_mem_educwork','avg_income','no_amty_sustenance',
                'no_amty_education','no_amty_transport','no_amty_healthcare','no_amty_finance',
                'no_amty_commerce','no_amty_entertainment','no_amty_other','lu_ind_commercial',
                'lu_ind_parks', 'lu_ind_industrial', 'lu_ind_agriculture','lu_ind_residential',
                'lu_ind_utilities', 'lu_ind_others']



        pre_tripgen_table = pd.DataFrame(columns=cols)

        for index, zone in enumerate(self.traffic_analysis_zones):
            pre_tripgen_table.loc[index] = zone.get_attr_vals2()

        #zone_info_json = json.dumps([ob.__dict__ for ob in self.traffic_analysis_zones], default=lambda o: o.__dict__, indent=4, sort_keys=True)
        return pre_tripgen_table, self.traffic_analysis_zones