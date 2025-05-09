SRC = ./creando_nodos/json_creator.py 
	
#SRC1 = ./creando_nodos/container_creator.py

CC = python3

RESET := \033[0m
RED := \033[1;31m
GREEN := \033[1;32m
YELLOW := \033[1;33m
BLUE := \033[1;34m
CYAN := \033[1;36m

define ART
$(CYAN)  


	     ┓┏•       ┓┳┓   ┓   
	     ┃┃┓┏┓╋┓┏┏┓┃┃┃┏┓┏┫┏┓┏
	     ┗┛┗┛ ┗┗┻┗┻┗┛┗┗┛┗┻┗ ┛
											
$(RED)

	Tecnologías de virtualización y 
automatización de nodos lógicos para subestaciones 
   eléctricas a partir de configuraciones SCL

$(RESET)

endef
export ART

all :
	@docker-compose down --remove-orphans
	@$(CC) $(SRC)
	@echo "$$ART"
	@docker-compose build 
	@docker-compose up -d
#	@$(CC) $(SRC1) 

.PHONY: activity-log dump-net both