#!/usr/bin/env Rscript
# Estatísticas básicas sobre áreas

setwd(DIR)

#Verificar se o arquivo de dados existe
if (file.exists("dados_farmtech.csv")) {
    dados <- read.csv("dados_farmtech.csv")

    #Exibir os dados carregados
    print("---- Dados Carregados do CSV ----")
    print(dados)

    # Calcula e exibe a média da área
    media_area <- mean(dados$Area_m2)
    print(paste("Média da área de plantio: ", round(media_area, 2), "m2"))

    # Calcula e exibe o desvio padrão da área
    desvio_padrao_area <- sd(dados$Area_m2)
    print(paste("Desvio padrão da área de plantio: ", round(desvio_padrao_area, 2), "m2"))

} else {
    print("Arquvio 'dados_farmtech.csv' não encotrado. Por Favor, execute o script Python e salve os dados primeiro.")
}