# -*- coding: utf-8 -*-
#
# Copyright 2020 - Viktor Gal
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import calamus.fields as fields
from calamus.schema import JsonLDSchema, blank_node_id_strategy
import marshmallow.fields as msmlfields
from calamus.fields import _JsonLDField


AQ_SCHEMA = fields.Namespace("http://odahub.io/ontology#")
XML_SCHEMA = fields.Namespace("http://www.w3.org/2001/XMLSchema#")
DC_TERMS = fields.Namespace("http://purl.org/dc/terms/")
RDFS = fields.Namespace("http://www.w3.org/2000/01/rdf-schema#")


class ParameterValue(_JsonLDField, msmlfields.Field):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        value = super()._serialize(value, attr, obj, **kwargs)
        if self.parent.opts.add_value_types:
            xsd_type = "xsd:anyURI"
            if type(value) == bool:
                xsd_type = "xsd:boolean"
            elif type(value) == int:
                xsd_type = "xsd:int"
            elif type(value) == float:
                xsd_type = "xsd:float"
            elif type(value) == str:
                xsd_type = "xsd:string"
            value = {"@type": xsd_type, "@value": value}
        return value

    def _deserialize(self, value, attr, data, **kwargs):
        v = json.loads(value)
        return v["@value"]


class EvaluationMeasure:
    def __init__(self, _id):
        self._id = _id


class EvaluationMeasureSchema(JsonLDSchema):
    _id = fields.Id()

    class Meta:
        rdf_type = AQ_SCHEMA.EvaluationMeasure
        model = EvaluationMeasure


class ModelEvaluation:
    def __init__(self, _id, value, specified_by):
        self._id = _id
        self.value = value
        self.specified_by = specified_by


class ModelEvaluationSchema(JsonLDSchema):
    _id = fields.Id()
    value = ParameterValue(AQ_SCHEMA.hasValue)
    specified_by = fields.Nested(AQ_SCHEMA.specifiedBy, EvaluationMeasureSchema)

    class Meta:
        rdf_type = AQ_SCHEMA.ModelEvaluation
        model = ModelEvaluation


class HyperParameter:
    def __init__(self, _id, model_hash):
        self._id = "http://www.w3.org/ns/mls#HyperParameter.{}.{}".format(
            _id, model_hash
        )
        self.label = _id


class HyperParameterSchema(JsonLDSchema):
    _id = fields.Id()
    label = fields.String(RDFS.label)

    class Meta:
        rdf_type = AQ_SCHEMA.HyperParameter
        model = HyperParameter


class Algorithm:
    def __init__(self, _id):
        self._id = _id
        self.label = _id


class AlgorithmSchema(JsonLDSchema):
    _id = fields.Id()
    label = fields.String(RDFS.label)

    class Meta:
        rdf_type = AQ_SCHEMA.Algorithm
        model = Algorithm



class HyperParameterSetting:
    def __init__(self, value, specified_by, model_hash):
        self._id = f"http://www.w3.org/ns/mls#HyperParameterSetting.{specified_by.label}.{model_hash}"
        self.value = value
        self.specified_by = specified_by


class HyperParameterSettingSchema(JsonLDSchema):
    _id = fields.Id()
    value = ParameterValue(AQ_SCHEMA.hasValue)
    specified_by = fields.Nested(
        AQ_SCHEMA.specifiedBy, HyperParameterSchema, only=("_id",)
    )

    class Meta:
        rdf_type = AQ_SCHEMA.HyperParameterSetting
        model = HyperParameterSetting
        add_value_types = True


class Implementation:
    """Repesent an ML Schema defined Model."""

    def __init__(self, _id, parameters, implements=None, version=None, name=None):
        self._id = _id
        self.name = name
        self.parameters = parameters
        self.implements = implements
        self.version = version


class ImplementationSchema(JsonLDSchema):
    _id = fields.Id()
    name = fields.String(DC_TERMS.title)
    parameters = fields.Nested(
        AQ_SCHEMA.hasHyperParameter, HyperParameterSchema, many=True
    )
    implements = fields.Nested(AQ_SCHEMA.implements, AlgorithmSchema)
    version = fields.String(DC_TERMS.hasVersion)

    class Meta:
        rdf_type = AQ_SCHEMA.Implementation
        model = Implementation


class AstrophysicalObject:
    """Repesent an AstrophysicalObject Schema"""

    def __init__(self, _id, name):
        self._id = _id
        self.name = name


class AstrophysicalObjectSchema(JsonLDSchema):
    _id = fields.Id()
    name = fields.String(DC_TERMS.title)
    #parameters = fields.Nested(
    #    AQ_SCHEMA.hasHyperParameter, HyperParameterSchema, many=True
    #)
    #implements = fields.Nested(AQ_SCHEMA.implements, AlgorithmSchema)
    #version = fields.String(DC_TERMS.hasVersion)

    class Meta:
        rdf_type = AQ_SCHEMA.AstrophysicalObject
        model = AstrophysicalObject


class AstroqueryModule:
    """Repesent an AstrophysicalObject Schema"""

    def __init__(self, _id, name):
        self._id = _id
        self.name = name
        

class AstroqueryModuleSchema(JsonLDSchema):
    _id = fields.Id()
    name = fields.String(DC_TERMS.title)
    #parameters = fields.Nested(
    #    AQ_SCHEMA.hasHyperParameter, HyperParameterSchema, many=True
    #)
    #implements = fields.Nested(AQ_SCHEMA.implements, AlgorithmSchema)
    #version = fields.String(DC_TERMS.hasVersion)

    class Meta:
        rdf_type = AQ_SCHEMA.AstroqueryModule
        model = AstroqueryModule


class SkyCoordinates:
    """Repesent a SkyCoordinates Schema"""

    def __init__(self, _id, name):
        self._id = _id
        self.name = name


class SkyCoordinatesSchema(JsonLDSchema):
    _id = fields.Id()
    name = fields.String(DC_TERMS.title)

    class Meta:
        rdf_type = AQ_SCHEMA.SkyCoordinates
        model = SkyCoordinates


class Coordinates:
    def __init__(self, _id, name):
        self._id = _id
        self.name = name


class CoordinatesSchema(JsonLDSchema):
    _id = fields.Id()
    name = fields.String(DC_TERMS.title)

    class Meta:
        rdf_type = AQ_SCHEMA.Coordinates
        model = Coordinates


class Position:
    def __init__(self, _id, name):
        self._id = _id
        self.name = name


class PositionSchema(JsonLDSchema):
    _id = fields.Id()
    name = fields.String(DC_TERMS.title)

    class Meta:
        rdf_type = AQ_SCHEMA.Position
        model = Position


class Angle:

    def __init__(self, _id, name):
        self._id = _id
        self.name = name


class AngleSchema(JsonLDSchema):
    _id = fields.Id()
    name = fields.String(DC_TERMS.title)

    class Meta:
        rdf_type = AQ_SCHEMA.Angle
        model = Angle


class Pixels:

    def __init__(self, _id, name):
        self._id = _id
        self.name = name


class PixelsSchema(JsonLDSchema):
    _id = fields.Id()
    name = fields.String(DC_TERMS.title)

    class Meta:
        rdf_type = AQ_SCHEMA.Pixels
        model = Pixels


class ImageBand:

    def __init__(self, _id, name):
        self._id = _id
        self.name = name


class ImageBandSchema(JsonLDSchema):
    _id = fields.Id()
    name = fields.String(DC_TERMS.title)

    class Meta:
        rdf_type = AQ_SCHEMA.ImageBand
        model = ImageBand


class AstrophysicalRegion:
    def __init__(self, _id, name):
        self._id = _id
        self.name = name


class AstrophysicalRegionSchema(JsonLDSchema):
    _id = fields.Id()
    name = fields.String(DC_TERMS.title)

    isUsingSkyCoordinates = fields.Nested(
        AQ_SCHEMA.isUsingSkyCoordinates, SkyCoordinatesSchema, many=True, flattened=True
    )
    isUsingRadius = fields.Nested(
        AQ_SCHEMA.isUsingRadius, AngleSchema, many=True, flattened=True
    )

    class Meta:
        rdf_type = AQ_SCHEMA.AstrophysicalRegion
        model = AstrophysicalRegion


class AstrophysicalImage:
    def __init__(self, _id, name):
        self._id = _id
        self.name = name


class AstrophysicalImageSchema(JsonLDSchema):
    _id = fields.Id()
    name = fields.String(DC_TERMS.title)

    isUsingPosition = fields.Nested(
        AQ_SCHEMA.isUsingPosition, PositionSchema, many=True, flattened=True
    )
    isUsingCoordinates = fields.Nested(
        AQ_SCHEMA.isUsingCoordinates, CoordinatesSchema, many=True, flattened=True
    )
    isUsingRadius = fields.Nested(
        AQ_SCHEMA.isUsingRadius, AngleSchema, many=True, flattened=True
    )
    isUsingPixels = fields.Nested(
        AQ_SCHEMA.isUsingPixels, PixelsSchema, many=True, flattened=True
    )
    isUsingImageBand = fields.Nested(
        AQ_SCHEMA.isUsingImageBand, ImageBandSchema, many=True, flattened=True
    )

    class Meta:
        rdf_type = AQ_SCHEMA.AstrophysicalImage
        model = AstrophysicalImage


class Run:
    def __init__(
        self,
        _id,
        executes=None,
        input_values=[],
        output_values=[],
        realizes=None,
        version=None,
        name=None,
    ):
        self._id = _id
        self.executes = executes
        self.input_values = input_values
        self.output_values = output_values
        self.realizes = realizes
        self.version = version
        self.name = name


class RunSchema(JsonLDSchema):
    _id = fields.Id()
    executes = fields.Nested(AQ_SCHEMA.executes, ImplementationSchema)
    isUsing = fields.Nested(
        AQ_SCHEMA.isUsing, AstroqueryModuleSchema, many=True, flattened=True
    )

    isRequestingAstroObject = fields.Nested(
        AQ_SCHEMA.isRequestingAstroObject, AstrophysicalObjectSchema, many=True, flattened=True
    )

    isRequestingAstroRegion = fields.Nested(
        AQ_SCHEMA.isRequestingAstroRegion, AstrophysicalRegionSchema, many=True, flattened=True
    )

    isRequestingAstroImage = fields.Nested(
        AQ_SCHEMA.isRequestingAstroImage, AstrophysicalImageSchema, many=True, flattened=True
    )

    version = fields.String(DC_TERMS.hasVersion)
    name = fields.String(DC_TERMS.title)

    class Meta:
        rdf_type = AQ_SCHEMA.Run
        model = Run


