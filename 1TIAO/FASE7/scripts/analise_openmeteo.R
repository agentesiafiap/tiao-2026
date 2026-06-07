#!/usr/bin/env Rscript

# 1. Definir pacotes necessários
pacotes_necessarios <- c("httr", "jsonlite")

# 2. Verificar e instalar pacotes em falta silenciosamente
pacotes_em_falta <- pacotes_necessarios[!(pacotes_necessarios %in% installed.packages()[,"Package"])]
if(length(pacotes_em_falta) > 0) {
    message("A instalar dependências do R em falta: ", paste(pacotes_em_falta, collapse = ", "))
    install.packages(pacotes_em_falta, repos = "http://cran.rstudio.com/", quiet = TRUE)
}

# 3. Carregar pacotes
invisible(lapply(pacotes_necessarios, require, character.only = TRUE))

# 4. Configurar coordenadas da exploração agrícola (Exemplo configurado)
lat <- "-12.9714"
lon <- "-38.5014"

url <- paste0("https://api.open-meteo.com/v1/forecast?latitude=", lat, "&longitude=", lon, "&current_weather=true")

# 5. Executar o pedido à API
resposta <- GET(url)

if (status_code(resposta) == 200) {
    dados_clima <- fromJSON(content(resposta, "text", encoding = "UTF-8"))
    
    cat("---- Dados Meteorológicos Atuais (Open-Meteo) ----\n")
    cat("Temperatura: ", dados_clima$current_weather$temperature, "°C\n")
    cat("Velocidade do Vento: ", dados_clima$current_weather$windspeed, "km/h\n")
    cat("Direção do Vento: ", dados_clima$current_weather$winddirection, "°\n")
    cat("Hora da Leitura: ", dados_clima$current_weather$time, "\n")
} else {
    cat("Erro ao consultar a API Open-Meteo. Código de status: ", status_code(resposta), "\n")
}