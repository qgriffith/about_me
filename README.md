[![Manually build and deploy](https://github.com/qgriffith/about_me/actions/workflows/build-deploy-manual.yml/badge.svg)](https://github.com/qgriffith/about_me/actions/workflows/build-deploy-manual.yml)

# About_Me

### Description 
This code base manages my [personal](https://qgriffith.me) site using a [Hugo](https://gohugo.io/) The site runs on with a AWS Cloudfront that is backed by an S3 bucket and created with terraform. There is python code the pulls data from both [peloton](https://www.onepeloton.com/) and [strava](https://www.strava.com/) API to populate a static page with my most recent data.

### Deployment
Deplyment is managed via Github Actions and is automatically deploy the website when changes are merged to the master branch on Bitbucket.

#### TODO
* Add Unit test to the python script
* Turn the python script into modules
* Enhance the look of the peloton/strava pages
* ~~Add a step in the pipeline to invalidate CF cache on deploy~~
* ~~Add logging output to the python script~~
* ~~Look at switching to GitHub Actions~~
* ~~Add Strava data to the python script~~
* ~~Add a custom task to the pipeline that only generats the new data~~
* ~~Remove the hugo step that stubs out the template and move it to python to auto-generate~~
* ~~Add a link to the Peloton class~~
* ~~Pull the full day of classes instead of the most recent single class~~
