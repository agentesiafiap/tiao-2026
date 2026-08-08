library(httr)
library(jsonlite)

# Adicionar menu para entrada de dados
cat("\n*** Bem-vindo ao coletor de dados meteorológicos! ***\n")
cat("\nPor favor, insira as informações da localização desejada.\n")

# Solicitar nome da cidade ao usuário
cidade <- readline(prompt = "\nDigite o nome da cidade: ")

# Solicitar latitude e longitude ao usuário
latitude <- as.numeric(readline(prompt = "\nDigite a latitude: "))
longitude <- as.numeric(readline(prompt = "\nDigite a longitude: "))

# Verificar se os valores inseridos são válidos
if (is.na(latitude) || is.na(longitude)) {
  stop("Erro: Latitude ou longitude inválida. Por favor, insira valores numéricos.")
}

# Definir a URL base da API e os parâmetros
base_url <- "https://api.open-meteo.com/v1/forecast"

# Atualizar os parâmetros com os valores fornecidos pelo usuário
params <- list(
  latitude = latitude,
  longitude = longitude,
  hourly = "temperature_2m,precipitation",
  current_weather = TRUE,
  timezone = "auto"
)

# Fazer a requisição GET
response <- GET(base_url, query = params)

# Verificar se a requisição foi bem-sucedida
if (status_code(response) == 200) {
  # Parsear o conteúdo da resposta
  data <- content(response, as = "parsed", type = "application/json")
  
  # Extrair informações relevantes
  current_weather <- data$current_weather
  temperature <- current_weather$temperature
  windspeed <- current_weather$windspeed
  weather_time <- current_weather$time
  
  # Exibir as informações no terminal
  cat("Informações Meteorológicas:\n")
  cat("---------------------------\n")
  cat(sprintf("Cidade: %s\n", cidade))
  cat(sprintf("Temperatura Atual: %.1f°C\n", temperature))
  cat(sprintf("Velocidade do Vento: %.1f km/h\n", windspeed))
  cat(sprintf("Horário da Medição: %s\n", weather_time))
  
} else {
  # Exibir mensagem de erro
  cat("Erro ao acessar a API. Código de status:", status_code(response), "\n")
}