# Rscript para Análise Estatística e Visualização de Dados da FarmTech Solutions

# Instalação de pacotes se necessário (execute uma vez no RStudio ou R terminal)
if (!require(dplyr)) install.packages("dplyr")
if (!require(ggplot2)) install.packages("ggplot2")
if (!require(readr)) install.packages("readr")
if (!require(jsonlite)) install.packages("jsonlite") # Para exportar resultados se necessário

# Carrega as bibliotecas
library(dplyr)
library(ggplot2)
library(readr)

# --- 1. Definições de Arquivo ---
INPUT_FILE <- "r_analysis/dados_para_r.csv"
OUTPUT_IMAGE_DIR <- "./document" # Pasta para salvar imagens
OUTPUT_PLOT_FILENAME <- "boxplot_umidade_por_npk.png"

# Garante que o diretório de saída da imagem existe
if (!dir.exists(OUTPUT_IMAGE_DIR)) {
  dir.create(OUTPUT_IMAGE_DIR)
}

# --- 2. Carrega os Dados ---
print(paste("Lendo dados limpos para R em:", INPUT_FILE))
dados <- read_csv(INPUT_FILE, show_col_types = FALSE)

# Verifica se os dados foram carregados corretamente
if (nrow(dados) == 0) {
  stop("ERRO: Nenhum dado foi carregado do arquivo. Verifique o CSV.")
}

print(paste("Dados carregados. Número de observações:", nrow(dados)))

# --- 3. Análise Estatística Descritiva ---
print("\n=== Análise Estatística Descritiva ===")

# Umidade
umidade_stats <- dados %>%
  summarise(
    Media = mean(Umidade_DHT, na.rm = TRUE),
    Mediana = median(Umidade_DHT, na.rm = TRUE),
    Variancia = var(Umidade_DHT, na.rm = TRUE),
    Desvio_Padrao = sd(Umidade_DHT, na.rm = TRUE),
    Min = min(Umidade_DHT, na.rm = TRUE),
    Max = max(Umidade_DHT, na.rm = TRUE)
  )
print("\n--- Umidade do Solo (DHT) ---")
print(umidade_stats)

# Valor LDR (simulando pH)
ldr_stats <- dados %>%
  summarise(
    Media = mean(Valor_LDR, na.rm = TRUE),
    Mediana = median(Valor_LDR, na.rm = TRUE),
    Variancia = var(Valor_LDR, na.rm = TRUE),
    Desvio_Padrao = sd(Valor_LDR, na.rm = TRUE),
    Min = min(Valor_LDR, na.rm = TRUE),
    Max = max(Valor_LDR, na.rm = TRUE)
  )
print("\n--- Valor do LDR (pH Simulado) ---")
print(ldr_stats)

# Índice NPK (Soma de N, P, K presentes)
npk_indice_stats <- dados %>%
  summarise(
    Media = mean(Indice_NPK, na.rm = TRUE),
    Mediana = median(Indice_NPK, na.rm = TRUE),
    Variancia = var(Indice_NPK, na.rm = TRUE),
    Desvio_Padrao = sd(Indice_NPK, na.rm = TRUE),
    Min = min(Indice_NPK, na.rm = TRUE),
    Max = max(Indice_NPK, na.rm = TRUE)
  )
print("\n--- Índice NPK (0=todos ausentes, 3=todos presentes) ---")
print(npk_indice_stats)


# --- 4. Análise de Score de Deficiência (Original do Projeto) ---
print("\n=== Análise de Score de Deficiência (Para a Cultura do Tomate) ===")

# Definir limites ideais para NPK, pH e Umidade para o Tomate
# NPK_Presente (1 para presente, 0 para ausente)
# PH_LDR (5.5 - 6.5 é ideal)
# Umidade_DHT (60% para baixo indica necessidade, 60-80% ideal para algumas análises)

# Calculando um score de deficiência para cada observação
dados <- dados %>%
  mutate(
    Deficiencia_N = ifelse(N_Presente == 0, 1, 0),
    Deficiencia_P = ifelse(P_Presente == 0, 1, 0),
    Deficiencia_K = ifelse(K_Presente == 0, 1, 0),
    Deficiencia_PH = ifelse(Valor_LDR < 5.5 | Valor_LDR > 6.5, 1, 0),
    Deficiencia_Umidade = ifelse(Umidade_DHT < 60, 1, 0) # Foco em umidade baixa
  )

dados$Score_Deficiencia_Total <- dados$Deficiencia_N +
                                 dados$Deficiencia_P +
                                 dados$Deficiencia_K +
                                 dados$Deficiencia_PH +
                                 dados$Deficiencia_Umidade

# Exibe o score médio ou total de deficiência
media_score_deficiencia <- mean(dados$Score_Deficiencia_Total, na.rm = TRUE)
print(paste("Score Médio de Deficiência Total:", round(media_score_deficiencia, 2)))

if (media_score_deficiencia > 2) { # Limite arbitrário para alerta
  print("ALERTA: O solo apresenta um alto score médio de deficiência. Irrigação pode ser comprometida.")
} else {
  print("Boas condições de solo detectadas em média.")
}

# --- 5. Visualização de Dados: Boxplot da Umidade por NPK ---
print(paste("\n=== Gerando Gráfico de Dispersão: Umidade vs. pH (Decisão da Bomba) ==="))

# Prepara a variável da Bomba para o rótulo
dados$Bomba_Status <- factor(dados$Bomba_Ligada,
                             levels = c(0, 1),
                             labels = c("DESLIGADA", "LIGADA"))

scatterplot_decisao <- ggplot(dados, aes(x = Umidade_DHT, y = Valor_LDR, color = Bomba_Status)) +
  geom_point(alpha = 0.7, size = 3) +
  
  # Adicionar linhas de referência da Lógica de Decisão (Tomate)
  # Umidade de Corte: 60%
  geom_vline(xintercept = 60, linetype = "dashed", color = "gray50") +
  # pH de Corte (LDR Valor): 5.5 e 6.5
  geom_hline(yintercept = 5.5, linetype = "dashed", color = "gray50") +
  geom_hline(yintercept = 6.5, linetype = "dashed", color = "gray50") +

  labs(
    title = "Fronteira de Decisão de Irrigação (Umidade vs. pH/LDR)",
    x = "Umidade do Solo (%)",
    y = "Leitura LDR (pH Simulado)",
    color = "Status da Bomba"
  ) +
  theme_minimal() +
  scale_color_manual(values = c("DESLIGADA" = "#ff4d4d", "LIGADA" = "#20b2aa")) # Vermelho para desligado, Verde-água para ligado

# Salva o gráfico em um arquivo PNG
output_image_path <- file.path(OUTPUT_IMAGE_DIR, "scatterplot_decisao.png")
ggsave(output_image_path, plot = scatterplot_decisao, width = 10, height = 7, dpi = 300)
print(paste("Gráfico de Dispersão salvo em:", output_image_path))

print("\n--- Análise R Concluída ---")