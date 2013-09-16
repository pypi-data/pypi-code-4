
intersphinx = (
    ("{DEVELOP_ROOT}/docs/build/html/", None),
    ("http://pythonhosted.org/orangecontrib.earth/", None),
)

from Orange.OrangeWidgets.Data import OWRank
from .. import earth


def earth_score_measure():
    if not hasattr(OWRank, "SCORES") or earth.ScoreEarthImportance in \
            [m.score for m in OWRank.SCORES]:
        return None

    params = [
        {"name": "t",
         "type": int,
         "display_name": "Num. models.",
         "range": (1, 20),
         "default": 10,
         "doc": "Number of models to train for feature scoring."},
        {"name": "terms",
         "type": int,
         "display_name": "Max. num of terms",
         "range": (3, 200),
         "default": 10,
         "doc": "Maximum number of terms in the forward pass"},
        {"name": "degree",
         "type": int,
         "display_name": "Max. term degree",
         "range": (1, 3),
         "default": 2,
         "doc": "Maximum degree of terms included in the model."}
    ]

    return OWRank.score_meta(
        name="Earth Importance",
        shortname="Earth imp.",
        score=earth.ScoreEarthImportance,
        params=params,
        supports_regression=True,
        supports_classification=True,
        handles_discrete=True,
        handles_continuous=True,
    )

EARTH_SCORE = earth_score_measure()
