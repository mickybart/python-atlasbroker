Docker
------

This part can be extracted to a new project to manage your own Atlas broker deployment
with custom Config and secrets management.

Create image
^^^^^^^^^^^^

.. code:: bash
    
    export VERSION=1
    docker build -t atlas-broker:$VERSION .


