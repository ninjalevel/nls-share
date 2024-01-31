> C:\DHE\git\nls-infra\root\Atmos2\AWS\_asBuilt.md

# Geodesic: C:\DHE\git\nls-infra\root\_init\geodesic

# Atmos Config

- Configure 'root\Atmos2\AWS\system_config.sh'

- Configure atmos.yaml


- https://atmos.tools/design-patterns/inline-component-customization
```bash
cd stacks ; mkdir default ; cd default
touch vpc-flow-logs-bucket.yaml ; touch vpc.yaml
cd ..
touch dev.yaml ;touch staging.yaml ;touch prod.yaml

# `dev` stack
atmos terraform deploy vpc -s dev

```
# Configure C:\DHE\git\nls-infra\root\Atmos2\AWS\vendor.yaml
atmos vendor pull

