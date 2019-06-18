# Vision Service

This is a simple REST service used to host pre-trained [Keras](https://keras.io) models. The service consists of three modules running in separate [Docker](https://www.docker.com/) containers: a REST API which is developed using [Flask](http://flask.pocoo.org/) microframework and is running behind [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) server, a model server, and [Redis](https://redis.io) database used to store images and corresponding predictions. The entire stack can be easily deployed using provided [Docker Compose](https://docs.docker.com/compose/) files.

The REST API handles user requests with image files and passes them to Redis database. The model server constantly fetches images from Redis, makes batch predictions using a pre-trained Keras model, and stores the results back to Redis. Once the results are ready for the submitted image, the web service sends predictions to the user in JSON response.

The project is inspired by this [blog post](https://blog.keras.io/building-a-simple-keras-deep-learning-rest-api.html).

## Deployment

First, install [Docker](https://docs.docker.com/install/) and [Docker Compose](https://docs.docker.com/compose/install/) by following instructions from the official websites. Once you have Docker installed, everything is ready for deployment.

### Development

In order to start the service in development mode, execute the following command from the project's root directory:
```bash
docker-compose up
```
The service should be up and running on 8080 port.

### Production

In production, run the following command instead:
```bash
docker-compose -f docker-compose.yml -f docker-compose.production.yml up -d
```

## Usage

Once the service is up and running, you can use `curl` to make a prediction request:

![](../assets/sample.jpg?raw=true)

```bash
curl -F image=@sample.jpg http://localhost:8080/api/predict
```
The JSON response will look something like this:
```json
{
  "success": true,
  "message": {
    "predictions": [
      {
        "label": "tiger_cat",
        "proba": 0.3253738582134247
      },
      {
        "label": "tabby",
        "proba": 0.315514475107193
      },
      {
        "label": "Egyptian_cat",
        "proba": 0.12767720222473145
      },
      {
        "label": "Persian_cat",
        "proba": 0.1148894876241684
      },
      {
        "label": "lynx",
        "proba": 0.019103804603219032
      }
    ],
    "predicted_at": "20190618_162447"
  }
}
```
