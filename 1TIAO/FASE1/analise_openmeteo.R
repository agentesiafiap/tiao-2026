#!/usr/bin/env Rscript
# Coleta meteorológica via Open-Meteo (sem API key)
# Exemplo: Salvador/BA (-12.97, -38.50)

suppressWarnings(suppressMessages({
library(httr)
library(jsonlite)
}))

lat <- -12.97
lon <- -38.50

url <- sprintf("https://api.open-meteo.com/v1/forecast?latitude=%f&longitude=%f&current_weather=true&hourly=temperature_2m,precipitation&timezone=auto", lat, lon)
res <- httr::GET(url)
stop_for_status(res)
js <- fromJSON(content(res, as="text", encoding="UTF-8"))

cat("\n=== METEOROLOGIA (Open-Meteo) ===\n")
cat(sprintf("Local (lat,lon): %.2f, %.2f\n", lat, lon))

if (!is.null(js$current_weather)) {
cw <- js$current_weather
cat(sprintf("Agora: Temp %.1f°C | Vento %.1f km/h | Direção %d°\n", cw$temperature, cw$windspeed, cw$winddirection))
}

if (!is.null(js$hourly)) {
cat("\nPróximas horas (temperatura, precipitação):\n")
df <- data.frame(time = js$hourly$time,
temp = js$hourly$temperature_2m,
precip = js$hourly$precipitation)
head_n <- min(8, nrow(df))
print(head(df, head_n))
}