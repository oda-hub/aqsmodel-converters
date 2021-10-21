import gorilla # TODO: use this?

from .models import (
    AstrophysicalObject,
    AstrophysicalRegion,
    AstroqueryModule,
    SkyCoordinates,
    Angle,
    Run,
    RunSchema,
)
from .common import fn_args_as_params, mls_add_param
from .io import log_renku_aqs
from distutils.version import LooseVersion
from uuid import uuid1
import random
import json


def standardize_types(v):
    if isinstance(v, np.ndarray):
        return [normalize_float(x) for x in v.tolist()]
    elif isinstance(v, float):
        return normalize_float(v)
    elif callable(v):
        return str(v)  # TODO
    elif isinstance(v, rv_frozen):
        return {"dist_name": v.dist.name, "args": v.args, "kwds": v.kwds}
    return v

def autolog():
    import astroquery
    astroquery.hooked = True
    print("astrquery.hooked: ", str(getattr(astroquery, 'hooked')))

    import astroquery.query

    def produce_annotation(self, aq_query_type, *args, **kwargs):
        aq_module_name = self.__class__.__name__    

        print(f"\033[33mpatched {aq_query_type} with:\033[0m", args, kwargs)    
        print("\033[33mwriting annotation here:\033[0m", aq_module_name, args, kwargs)    

        run_id = uuid1()
        run = Run(_id=run_id,
                  name=aq_query_type + "_" + str(run_id))
        
        aq_module = AstroqueryModule(_id="https://odahub.io/ontology#AQModule" + aq_module_name,
                                     name=aq_module_name)

        #run.input_values = [AstrophysicalObject(_id=aq_module_name, name=aq_module_name)]
        run.isUsing = [aq_module]

        if aq_query_type == "query_object":
            obj_name = args[0]
            obj =  AstrophysicalObject(_id="https://odahub.io/ontology#AstroObject" + obj_name.replace(" ","_"),
                                       name=obj_name) # normalize id
            run.isRequestingAstroObject = [obj]

        # TODO capture also query_region ?
        if aq_query_type == "query_region":
            if 'source' in kwargs:
                coordinates = kwargs['source']
            else:
                coordinates = args[0]

            skycoord_obj = SkyCoordinates(_id="https://odahub.io/ontology#SkyCoordinates" + repr(coordinates).replace(" ","_"),
                           name=repr(coordinates))

            radius = None
            if 'radius' in kwargs:
                radius = kwargs['radius']
            else:
                if args[1] is not None:
                    radius = args[1]

            radius_obj = Angle(_id="https://odahub.io/ontology#Angle" + repr(radius).replace(" ","_"),
                           name=repr(radius))

            astro_region_name = radius_obj.name + " " + skycoord_obj.name
            # definition of the astro region
            astro_region_obj = AstrophysicalRegion(_id="https://odahub.io/ontology#AstroRegion" + astro_region_name.replace(" ","_"),
                                       name=astro_region_name)
            astro_region_obj.isUsingSkyCoordinates = skycoord_obj
            astro_region_obj.isUsingRadius = radius_obj

            run.isRequestingAstroRegion = [astro_region_obj]

        # extra stuff for debug
        run.aq_module_name = aq_module_name
        run.aq_query_type = aq_query_type
        run.aq_args = args
        run.aq_kwargs = kwargs

        log_renku_aqs(
            RunSchema().dumps(run), str(self.__hash__()), 
            force=True,
            run=run
        )        

    # aq hook
    def aqs_query_object(self, *args, **kwargs):
        produce_annotation(self, 'query_object', *args, **kwargs)

        return object.__getattribute__(self, 'query_object')(*args, **kwargs)

    # aq hook
    def aqs_query_region(self, *args, **kwargs):
        produce_annotation(self, 'query_region', *args, **kwargs)

        return object.__getattribute__(self, 'query_region')(*args, **kwargs)        

    # hook on aq hook    
    def asq_BaseQuery_getattribute(self, name):
        if name == "query_object":
            return lambda *a, **aa: aqs_query_object(self, *a, **aa)

        if name == "query_region":
            return lambda *a, **aa: aqs_query_region(self, *a, **aa)

        #print("\033[33mpatching BaseQuery_getattr!\033[0m", name)
        return object.__getattribute__(self, name)

    astroquery.query.BaseQuery.__getattribute__ = asq_BaseQuery_getattribute


