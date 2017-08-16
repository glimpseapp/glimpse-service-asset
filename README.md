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
Build docker image and push to Google container registry
```
docker build -t gcr.io/glimpse-123456/glimpse-service-asset .
gcloud docker -- push gcr.io/glimpse-123456/glimpse-service-asset
```
*Note: the the*


*Update openapi.yaml and deploy*
```gcloud service-management deploy openapi.json```

After you run the command above get the CONFIG_ID of the service you just deployed, it looks something like 2017-08-10r6. 
Add the CONFIG_ID to the kube-deployment.yaml into the -v argument:
```
      - name: esp
        image: gcr.io/endpoints-release/endpoints-runtime:1
        args: [
          "-p", "8081",
          "-a", "127.0.0.1:5000",
          "-s", "glimpse-service-asset.endpoints.glimpse-123456.cloud.goog",
          "-v", "[CONFIG_ID]",
        ]
``` 

*Update kubernetes file and deploy*
```
kubectl apply -f kube-deployment.yaml
kubectl apply -f kube-service.yaml
```

Get the service IP for the asset service and update the openapi:
```
kc get service
```

Update the following openapi field:
```
  "x-google-endpoints": [
    {
      "name": "glimpse-service-asset.endpoints.glimpse-123456.cloud.goog",
      "target": [SERVICE EXTERNAL IP]
    }
  ],
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


Check this tutorial in case of doubt: shttps://jhipster.github.io/tips/018_tip_kubernetes_and_google_cloud_sql.html 
