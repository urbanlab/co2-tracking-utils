FROM node:lts-alpine AS dev

WORKDIR /app

COPY src/ /app/src
COPY static/ /app/static
COPY eslint.config.js /app/eslint.config.js
COPY package*.json /app/
COPY svelte.config.js /app/svelte.config.js
COPY tsconfig.json /app/tsconfig.json
COPY vite.config.ts /app/vite.config.ts

RUN npm install

EXPOSE 5173

ENTRYPOINT [ "npm", "run", "dev", "--", "--host", "0.0.0.0" ]

FROM node:lts-alpine AS build

WORKDIR /app

# copy node modules and all files from dev stage
COPY --from=dev /app/ /app/

RUN npm run build

FROM node:lts-alpine AS prod

WORKDIR /app

COPY --from=build /app/build /app
COPY --from=build /app/package*.json /app/

RUN npm ci --production

EXPOSE 3000

CMD [ "node", "index.js" ]
