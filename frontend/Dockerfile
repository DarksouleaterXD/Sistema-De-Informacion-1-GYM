FROM node:20-alpine

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar el resto del proyecto
COPY . .

# Exponer el puerto
EXPOSE 3000

# Comando por defecto (modo desarrollo)
CMD ["npm", "run", "dev"]
