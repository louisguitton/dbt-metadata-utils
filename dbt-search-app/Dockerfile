FROM node:16 as build-stage

WORKDIR /app

COPY dbt-search-app/package*.json .
RUN npm install

COPY dbt-search-app/ .
RUN npm run build

FROM nginx:1.20

COPY --from=build-stage /app/dist/ /usr/share/nginx/html
COPY --from=build-stage /app/nginx.conf /etc/nginx/nginx.conf
