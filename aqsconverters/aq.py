import gorilla # TODO: use this?

from .models import (
    AstrophysicalObject,
    AstroqueryModule,
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

    import astroquery.query

    def produce_annotation(self, aq_query_type, *args, **kwargs):
        aq_module_name = self.__class__.__name__    

        print(f"\033[33mpatched {aq_query_type} with:\033[0m", args, kwargs)    
        print("\033[33mwriting annotation here:\033[0m", aq_module_name, args, kwargs)    

        run = Run(uuid1())
        
        aq_module = AstroqueryModule(_id="http://odahub.io/ontology#AQModule" + aq_module_name, name=aq_module_name)

        #run.input_values = [AstrophysicalObject(_id=aq_module_name, name=aq_module_name)]
        run.isUsing = [aq_module]

        if aq_query_type == "query_object":
            obj_name = args[0]
            obj =  AstrophysicalObject(_id="http://odahub.io/ontology#AstroObject" + obj_name.replace(" ","_"), name=obj_name) # normalize id
            run.isRequestingAstroObject = [obj]

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


