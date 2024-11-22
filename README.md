# API Estaciones de Carga - Bad Brains

En este repositorio está implementado el Backend completo en formato API que se encargaría de gestionar las distintas peticiones de los usuarios a la hora de gestionar las estaciones de carga. También está incluido el servicio de mapa para los puntos de interés
## Table of Contents

- [Características](#caracteristícas)
- [Instalación](#instalación)
- [Uso](#uso)
- [Contribuir](#contribuir)
- [License](#license)

## Caracteristícas

- **Arquitectura de Servicio**: El proyecto está organizado en distintos contenedores para poder ser desplegado como servicio, utilizando por ejemplo Docker.
- **Provisionamiento de API**: El servicio ofrece también una API programática para poder lanzar cada método.
- **Uso de BBDD Relacionales y No Relacionales**: La API hace uso de ambos tipos de BBDD para almacenar información relativa a los usuarios y sus peticiones.

## Instalación

Para lanzar la API en formato local:

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/alru28/bad-brains-api.git
   cd bad-brains-api/src
   ```

2. Lanzar los contenedores:
	```bash
    docker-compose up
	```
	
Esto lanzara el servicio y sus dependencias, como MongoDB o PostgreSQL.

## Uso

Once the installation is complete, you can access Deusto AI-Sec programatic API by opening your web browser and navigating to:

> http://localhost:8000/docs

## Contribuir

Las contribuciones son bienvenidas. Puedes hacerlo así:

- Crear un fork del repositorio
- Crear una branch donde incluir una nueva feature o un bug-fix.
- Realiza tus cambios y asegura que siguen el estilo de código del proyecto.
- Crea una pull-request para aprobar tus cambios.

Añade por favor documentación y tests para cada uno de los cambios realizados.

## License

Este proyecto se ciñe a la licencia Apache License. Puedes ver el fichero LICENSE para obtener más detalles.
