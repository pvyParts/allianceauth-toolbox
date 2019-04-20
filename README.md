# allianceauth-toolbox

toolbox of random stuff for [Alliance Auth](https://gitlab.com/allianceauth/allianceauth).

## Install 

With your auth venv active, install the django app with the following command 
```
pip install git+https://github.com/pvyParts/allianceauth-toolbox.git
```

add `'toolbox',` to your INSTALLED_APPS in your local.py

run migrations and restart auth

# Pilot Log

Blacklist and note service for eve entities, with comments and edit capability.

## Permisions

### View / Access Perms

`toolbox | eve note | Can view all eve notes` Can View the Pilot Log with non restricted notes

`toolbox | eve note | Can View restricted eve notes` Can View the Pilot Log with restricted notes

`toolbox | eve note | Can View ultra_restricted eve notes` Can View the Pilot Log with ultra restricted notes

`toolbox | eve note | Can add new eve notes` Can add/edit new/existing items to the Pilot Log

`toolbox | eve note | Can Add restricted eve notes` Can add/edit new/existing restricted items to the Pilot Log

`toolbox | eve note | Can Add ultra_restricted eve notes` Can add/edit new/existing ultra restricted items to the Pilot Log

`toolbox | eve note | Can View the Blacklist` Can View the Blacklist 

`toolbox | eve note | Can add to Blacklist` Can add to the Blacklist 

`toolbox | eve note comment | Can view eve note comments` Can view comments to an entity in the Pilot Log

`toolbox | eve note comment | Can add comments on eve notes` Can add/view comments to an entity in the Pilot Log

`toolbox | eve note comment | Can view restricted eve note comments` Can view restricted comments on an entity in the Pilot Log

`toolbox | eve note comment | Can add new restricted comments to eve notes` Can add/view restricted comments to an entity in the Pilot Log

### Model admin perms 

`toolbox | eve note | Can add eve note` can add eve note in admin

`toolbox | eve note | Can change eve note` can change eve note in admin

`toolbox | eve note | Can delete eve note` can delete eve note in admin

`toolbox | eve note comment | Can add eve note comment` can add eve note comment in admin

`toolbox | eve note comment | Can change eve note comment` can change eve note comment in admin

`toolbox | eve note comment | Can delete eve note comment` can delete eve note comment in admin

# Issues

Please remember to report any toolbox related issues using the issues on **this** repository.



