import click
import io
import rdflib
import owlready2 as owl


rdfs = owl.get_ontology("http://www.w3.org/2000/01/rdf-schema#").load()

oda = owl.get_ontology("http://odahub.io/ontology")

ivoauat = owl.get_ontology("http://www.ivoa.net/rdf/uat")


fno = owl.get_ontology("http://ontology.odahub.io/function.rdf").load()
fno.base_iri="https://w3id.org/function/ontology#"

renku = owl.get_ontology("https://swissdatasciencecenter.github.io/renku-ontology/")

with oda:
    class Workflow(owl.Thing):        
        pass

    class AstroqueryModule(owl.Thing):
        label = "astroquery module"

    class AstrophysicalRegion(owl.Thing):
        label = "astrophysical region"

    class AstrophysicalObject(owl.Thing):
        label = "astrophysical object"

    class SkyCoordinates(owl.Thing):
        pass

    class Angle(owl.Thing):
        pass

    #class moduleRepresents(owl.ObjectProperty):
    #    domain = [AstroqueryModule]
    #    range = ivoauat['ivoauat']

    class isUsing(owl.ObjectProperty):
        # common?
        domain     = [Workflow]
        range    = [owl.Thing]
                
    class isRequesting(isUsing):
        domain     = [Workflow]
        range    = [AstrophysicalObject, AstroqueryModule, SkyCoordinates]
        
    class isRequestingParameter(isRequesting):
        pass

    class isRequestingAstroObject(isRequestingParameter):
        range    = [AstrophysicalObject]

    class isRequestingAstroRegion(isRequestingParameter):
        range    = [AstrophysicalRegion]

@click.group("owl")
def cli():
    pass

@cli.command()
def generate():
    f = io.BytesIO()
    oda.save(f, format="rdfxml")

    G = rdflib.Graph()
    G.parse(
        data=f.getvalue().decode(), format="xml")

    print(G.serialize(format="turtle").decode())


if __name__ == "__main__":
    cli()
