# About

In this directory you will be able to find drivers that could be installed on Kubernetes, you can choose any of them and run:

```sh
kubectl apply -f <driver-file-of-choice.yaml>
```

The YAML file configuration in the background will run a Job that will be able to apply the required files for the driver.