import gorilla # TODO: use this?

from .models import (
    AstrophysicalObject,
    AstrophysicalRegion,
    AstrophysicalImage,
    AstroqueryModule,
    SkyCoordinates,
    Angle,
    Pixels,
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
    from astropy import coordinates
    import hashlib

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

        if aq_query_type == "get_images":
            astro_image_name = ""
            astro_image_suffix = ""

            # coordinates
            skycoord_obj = None
            if 'coordinates' in kwargs:
                coordinates_arg = kwargs['coordinates']
                if coordinates_arg is not None:
                    if isinstance(coordinates_arg, coordinates.SkyCoord):
                        coordinates_arg_str = coordinates_arg.to_string()
                    else:
                        coordinates_arg_str = str(coordinates_arg)
                    skycoord_obj_id_suffix = hashlib.sha256(coordinates_arg_str.encode()).hexdigest()
                    astro_image_suffix += coordinates_arg_str
                    skycoord_obj = SkyCoordinates(_id="https://odahub.io/ontology#SkyCoordinates"
                                                      + skycoord_obj_id_suffix,
                                                  name=coordinates_arg_str)
                    astro_image_name += skycoord_obj.name

            # radius
            radius_obj = None
            if 'radius' in kwargs:
                radius_arg = kwargs['radius']
                if radius_arg is not None:
                    if isinstance(radius_arg, coordinates.Angle):
                        radius_arg_str = radius_arg.to_string()
                    else:
                        radius_arg_str = str(radius_arg)
                    radius_obj_id_suffix = hashlib.sha256(radius_arg_str.encode()).hexdigest()
                    astro_image_suffix += '_' + radius_arg_str
                    radius_obj = Angle(_id="https://odahub.io/ontology#Angle"
                                           + radius_obj_id_suffix,
                                       name=radius_arg_str)
                    astro_image_name += '_' + radius_obj.name

            # pixels
            pixels_obj = None
            if 'pixels' in kwargs:
                pixels = kwargs['pixels']
                if pixels is not None:
                    pixels_obj_id_suffix = hashlib.sha256(str(pixels).encode()).hexdigest()
                    pixels_obj = Pixels(_id="https://odahub.io/ontology#Pixels"
                                           + pixels_obj_id_suffix,
                                       name=str(pixels))
                    astro_image_name += '_' + pixels_obj.name
                    astro_image_suffix += '_' + str(pixels)

            # image_band
            image_band_obj = None
            if 'image_band' in kwargs:
                image_band = kwargs['image_band']
                if image_band is not None:
                    image_band_obj_id_suffix = hashlib.sha256(image_band.encode()).hexdigest()
                    image_band_obj = Pixels(_id="https://odahub.io/ontology#ImageBand"
                                           + image_band_obj_id_suffix,
                                       name=image_band)
                    astro_image_name += '_' + image_band_obj.name
                    astro_image_suffix += '_' + image_band

            astro_image_suffix = hashlib.sha256(astro_image_suffix.encode()).hexdigest()

            astro_image_obj = AstrophysicalImage(_id="https://odahub.io/ontology#AstroImage"
                                                       + astro_image_suffix,
                                                 name=astro_image_name)

            astro_image_obj.isUsingSkyCoordinates = [skycoord_obj]

            if radius_obj is not None:
                astro_image_obj.isUsingRadius = [radius_obj]

            if image_band_obj is not None:
                astro_image_obj.isUsingImageBand = [image_band_obj]

            if pixels_obj is not None:
                astro_image_obj.isUsingPixels = [pixels_obj]

            run.isRequestingAstroImage = [astro_image_obj]

        if aq_query_type == "query_object":
            obj_name = args[0]
            obj =  AstrophysicalObject(_id="https://odahub.io/ontology#AstroObject" + obj_name.replace(" ","_"),
                                       name=obj_name) # normalize id
            run.isRequestingAstroObject = [obj]

        if aq_query_type == "query_region":
            if 'coordinates' in kwargs:
                coordinates_arg = kwargs['coordinates']
            else:
                coordinates_arg = args[0]

            skycoord_obj_id_suffix = hashlib.sha256(coordinates_arg.to_string().encode()).hexdigest()
            skycoord_obj = SkyCoordinates(_id="https://odahub.io/ontology#SkyCoordinates"
                                              + skycoord_obj_id_suffix,
                                          name=coordinates_arg.to_string())

            radius_arg = None
            if 'radius' in kwargs:
                radius_arg = kwargs['radius']
            if radius_arg is not None:
                radius_obj_id_suffix = hashlib.sha256(radius_arg.to_string().encode()).hexdigest()
                radius_obj = Angle(_id="https://odahub.io/ontology#Angle"
                                       + radius_obj_id_suffix,
                                   name=radius_arg.to_string())

            astro_region_name = radius_obj.name + " " + skycoord_obj.name
            astro_region_suffix = hashlib.sha256((radius_arg.to_string() + "_" + coordinates_arg.to_string()).encode()).hexdigest()
            # definition of the astro region
            astro_region_obj = AstrophysicalRegion(_id="https://odahub.io/ontology#AstroRegion"
                                                       + astro_region_suffix,
                                       name=astro_region_name)
            astro_region_obj.isUsingSkyCoordinates = [skycoord_obj]
            astro_region_obj.isUsingRadius = [radius_obj]

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

        # aq hook
    def aqs_get_images(self, *args, **kwargs):
        produce_annotation(self, 'get_images', *args, **kwargs)

        return object.__getattribute__(self, 'get_images')(*args, **kwargs)

    # hook on aq hook    
    def asq_BaseQuery_getattribute(self, name):
        if name == "query_object":
            return lambda *a, **aa: aqs_query_object(self, *a, **aa)

        if name == "query_region":
            return lambda *a, **aa: aqs_query_region(self, *a, **aa)

        if name == "get_images":
            return lambda *a, **aa: aqs_get_images(self, *a, **aa)

        #print("\033[33mpatching BaseQuery_getattr!\033[0m", name)
        return object.__getattribute__(self, name)

    astroquery.query.BaseQuery.__getattribute__ = asq_BaseQuery_getattribute


