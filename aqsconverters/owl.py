import click
import io
import rdflib
import owlready2 as owl


rdfs = owl.get_ontology("http://www.w3.org/2000/01/rdf-schema#").load()

oda = owl.get_ontology("http://odahub.io/ontology")
fno = owl.get_ontology("http://ontology.odahub.io/function.rdf").load()
fno.base_iri="https://w3id.org/function/ontology#"

renku = owl.get_ontology("https://swissdatasciencecenter.github.io/renku-ontology/")

with oda:
    class Workflow(owl.Thing):
        pass

    class AstroqueryModule(owl.Thing):
        label = "astroquery module"

    class AstrophysicalObject(owl.Thing):
        label = "astrophysical object"

    class SkyCoordinates(owl.Thing):
        pass

                

    class isRequesting(owl.ObjectProperty):
        domain    = [AstrophysicalObject, AstroqueryModule, SkyCoordinates]
        range     = [Workflow]

    class isRequestingParameter(isRequesting):
        pass

    class isRequestingAstroObject(isRequestingParameter):
        domain    = [AstrophysicalObject]


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
