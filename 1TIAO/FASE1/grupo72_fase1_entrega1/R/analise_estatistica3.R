# Carregar os dados dos arquivos CSV
areas <- read.csv("areas_export.csv")
manejos <- read.csv("manejos_export.csv")

# Renomear colunas para evitar problemas com caracteres especiais
colnames(areas) <- c("Cultura", "Area_m2")
colnames(manejos) <- c("Cultura", "Produto", "Qtde_por_m", "Total_mL")

# Calcular estatísticas básicas para áreas
cat("\nEstatísticas para Áreas:\n")
cat("\nMédia da área:", mean(areas$Area_m2), "m²\n")
cat("Desvio padrão da área:", sd(areas$Area_m2), "m²\n")

# Calcular estatísticas básicas para manejos
cat("\nEstatísticas para Manejos:\n")
cat("\nMédia do total de produto necessário:", mean(manejos$Total_mL), "mL\n")
cat("Desvio padrão do total de produto necessário:", sd(manejos$Total_mL), "mL\n")