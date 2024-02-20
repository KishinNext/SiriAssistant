# Database pets

### how to run the project

1. Clone the repository
2. Install poetry
3. Install the dependencies
```pycon
poetry install
poetry install --with dev
```
4. generate jwt secret key #TODO add the command to generate the key
5. explain how autneticate in docs


How to run the agent?
To run, you need to add the credentials to the "development.yaml" file in the "auth/config" folder. The structure of the file is as follows:

```yaml
env: development
secrets:
  api_tokens:
    service:
    token:
  database:
    driver:
    host:
    port: 5432
    database:
    user:
    password:
```
Docker
With the "development.yaml" file ready, you can run the docker-compose to build and run the containers:

```angular2html
docker compose build --no-cache && docker compose -f docker-compose.yml up -d
```
