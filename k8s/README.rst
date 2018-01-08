k8s resources
=============

Atlas Broker Deployment
-----------------------

.. code:: bash
    
    export NS="atlas-broker"
    
    kubectl create ns $NS
    kubectl -n $NS apply -f atlas-broker-deployment.yaml
    kubectl -n $NS apply -f atlas-broker-svc.yaml
    
    # Declaration of the broker
    kubectl apply -f atlas-broker-clusterservicebroker.yaml
    
Test
----

Instance and Binding
^^^^^^^^^^^^^^^^^^^^

.. code:: bash
    
    kubectl create ns test-atlas-broker
    kubectl apply -f atlas-broker-instance.yaml
    kubectl apply -f atlas-broker-binding.yaml

Pod
^^^

The purpose is to demonstrate how to expose secrets set by the previous binding operation.

There is 3 ways to do it:
 - Individuals mapping (see env section)
 - Global mapping (see envFrom section)
 - File mapping (see volumeMounts/volumes)

.. code:: bash
    
    kubectl apply -f nginx.yaml
