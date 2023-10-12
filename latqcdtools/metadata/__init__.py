#
# metadata annotations
#
# D. Knuettel
#
# Metadata annotations that can be automatically exported.
#

import functools

_metadata_to_export = {}

def annotate_metadata(algo_name
                      , algo_doi=""
                      , algo_implementation="10.5281/zenodo.8241876"):
    meta = {
            "algorithm": {
                "reference": algo_doi
                , "implementation": algo_implementation
                # FIXME: get DOI to current version
                #        or explicitly state version somehow.
                }
            }
    def do_annotate(fnc):
        @functools.wraps(fnc)
        def with_metadata(*args, **kwargs):
            if(algo_name not in _metadata_to_export):
                # This takes ~40ns.
                _metadata_to_export[algo_name] = with_metadata._metadata
            return fnc(*args, **kwargs)

        # This is for when you want to inspect the metadata later.
        with_metadata._metadata = meta
        return with_metadata

    return do_annotate

def get_metadata_to_export():
    return [v for v in _metadata_to_export.values()]
