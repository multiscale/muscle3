###########
Change Log
###########

All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

Next
****

Changed
-------

* Fatal logic errors now throw instead of exiting, so that you have a chance
  to shut down the model cleanly before exiting.
* Instance.exit_error() was replaced by Instance.error_shutdown(), which no
  longer exits the process, it just shuts down the Instance.
* Central MUSCLE 3-managed settings are called settings everywhere now, not
  parameters. As a result, the API has changed in several places.


Added
-----


0.1.0
*****

Initial release of MUSCLE 3.

Added
-----
* Coupling different submodel instances
* Spatial and temporal scale separation and overlap
* Settings management
* Combining features
* Python support
* Initial distributed execution capability
