# Events Dashboard
Based on Tim's tutorial ([Youtube video link][yt]), which btw is a really good intro to Flask, authentification and databases! We built a kind of primitive social media/notice board where anyone can view the dashboard without an account.

The app was deployed using Amazon Elastic Beanstalk - [My events dashboard](http://test-environment.eba-ujxq6y6a.us-east-1.elasticbeanstalk.com/)

- You need to create a account to add or delete items
  - Only users who created the item/event can delete it
- Adding an image to each item is optional - all images are resized to a width of 620 pixels before being saved to the database
  - There is no image preview when adding a note, so do not fret


## Deploying locally
First install the required libraries (python 3.9)
```bash
pip install -r requirements.txt
```
Next launch the flask app
```bash
python application.py
```



### Learnings/Notes
- AWS scans for the variable `application` for deployment, so the Flask App bokject cannot bet named anything else
- AWS by default has a 3MB upload limit. This can be changed by specifying an `nginx` configuration file `<custom_config>.conf`, and an additional config file `<custom_config>.config` that tells the container to reload `nginx`
- [Elastic beanstalk access to s3](https://aws.amazon.com/premiumsupport/knowledge-center/elastic-beanstalk-s3-bucket-instance/)
- [Http to https](https://stackoverflow.com/questions/14693852/how-to-force-https-on-elastic-beanstalk)






[yt]: https://www.youtube.com/watch?v=dam0GPOAvVI