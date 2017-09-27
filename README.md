Glimpse Service Asset
====================

This service manage the asset upload and download


Install
-------
Install virtualenv and python dependencies
```
virtualenv -p python3 venv
. venv/bin/activate
```


Deploy
------

*Code changes*
When you change something in the code, you want to build the docker image and push to Google container registry,
then you want to deploy the kube-deployment to refresh the pod:  
```bash
docker build -t gcr.io/glimpse-123456/glimpse-service-asset .
gcloud docker -- push gcr.io/glimpse-123456/glimpse-service-asset
kubectl delete deployment glimpse-service-asset
kubectl apply -f kube-deployment.yaml
```

*Changes to the API*
To change the API you want to deploy the openapi.json file:
```bash
gcloud service-management deploy openapi.json
```

Then, you want to update the configuration in the kube-deployment:
```yaml
      - name: esp
        image: gcr.io/endpoints-release/endpoints-runtime:1
        args: [
          "-p", "8081",
          "-a", "127.0.0.1:5000",
          "-s", "asset.glimpse.online",
          "-v", "[CONFIG_ID]",
        ]
``` 

Finally you want to deploy the kubernetes deployment:
```bash
kubectl delete deployment glimpse-service-asset
kubectl apply -f kube-deployment.yaml
```

Deploy the service
------------------
To deploy the service and connect it to the Internet: 
```bash
kubectl apply -f kube-service.yaml
```

Get the IP of the service and update the CNAME in the DNS entry: 
```
kc get service
```


Run locally
-----------
```docker run -p 5000:80 gcr.io/glimpse-123456/glimpse-service-asset```

You may have also to port forward the services used by this microservice e.g.:
```
kubectl get pod
kubectl port-forward [CASSANDRA_POD_NAME] 9042:9042
```



Create Google Credentials Secret and mount the Volume to the Pod
----------------------------------------------------------------
*Skip all this step if the volume secret glimpse-credentials already exists*
```
kubectl get secret
```

**Create AIM and secret**

Create a service-account IAM and give editor permissions
```
gcloud iam service-accounts create glimpse-application --display-name="Glimpse application"
gcloud projects add-iam-policy-binding glimpse-123456 --member serviceAccount:glimpse-application@glimpse-123456.iam.gserviceaccount.com --role roles/editor
```

Check if the AIM is there:
```
gcloud iam service-accounts list
```

Create credentials file:
```
gcloud iam service-accounts keys create --iam-account glimpse-application@glimpse-123456.iam.gserviceaccount.com glimpse-credentials.json
```

Create secret:
```
kubectl create secret generic cloudsql-oauth-credentials --from-file=credentials.json=glimpse-credentials.json
```

**Mount the secret into the pod**
Open the kube-deployment.yaml file and add the volumeMounts in the container:
```
        volumeMounts:
        - name: credentials-volume
          mountPath: /secrets/google_credentials
          readOnly: true
```

And the volumes for the pod: 

```
      volumes:
      - name: credentials-volume
        secret:
          secretName: glimpse-credentials
```


Check this tutorial in case of doubt: https://jhipster.github.io/tips/018_tip_kubernetes_and_google_cloud_sql.html 
