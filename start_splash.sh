docker rm -f splash
docker run --name=splash -p 8050:8050 -d scrapinghub/splash
