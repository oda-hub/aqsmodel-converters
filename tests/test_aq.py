from pathlib import Path
import aqsconverters.aq
import json
import shutil

RENKU_BASE = ".renku"

def test_to_aqs():
    shutil.rmtree(RENKU_BASE)

    # user might not want to include this, see sitecustomize.py approach for transparent loading
    # it's feasible if renku pre_run hook can modify the tool to set the path accordingly
    aqsconverters.aq.autolog()


    # this is what users typically run 
    import astroquery.simbad
    astroquery.simbad.Simbad.query_object("Crab")

    # this is what users typically run 
    #import astroquery.sdss
    #astroquery.sdss.SDSS.query_region("0 0", radius="0.01 deg")

    # check
    for fn in Path(RENKU_BASE).rglob("*json*"):        
        j = json.load(open(fn))
        print(fn, ": \n", json.dumps(j, sort_keys=True, indent=4))

