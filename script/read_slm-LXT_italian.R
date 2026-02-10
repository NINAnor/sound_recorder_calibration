library(readxl)
library(ggplot2)

#### Import data ####
file_lxt <- "C:/Users/julia.wiel/OneDrive - NINA/Documents/CALIBRATION/analysis/data/raw/LxT_0003857-20260202 142124-LxT_Data.004.xlsx"
slm_data <- readxl::read_excel(file_lxt, sheet = "Profilo storico")


# Select 1/3 octave
slm_data_3oct <- slm_data[1:8]
slm_data_3oct <- cbind(slm_data_3oct, slm_data[21:56])

freq_3oct <- c(8, 10, 12.5, 16, 20, 25, 31.5, 40, 50, 63, 80,
          100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500,
          3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000, 20000)


#### Plot frequency response for one specific time ####

# User enter row of interest
row = 6

# Select data
resp <- slm_data_3oct[,10:44]

freq_data <- data.frame(
  frequency = freq_3oct,
  response = as.numeric(resp[row,])
)

# Plot
ggplot(freq_data, aes(x = frequency, y = response)) +
  geom_line(color = "blue") +
  geom_point(color = "red", size = 2) +
  geom_text(aes(label = frequency), vjust = -1, size = 3) +
  scale_x_log10() +
  labs(x = "Frequency (Hz) - Log Scale", y = "Sound Level (dB)") + 
  ggtitle("SLM frequency-response", 
          subtitle = paste("1/3 octave from 8Hz to 20000Hz for row number: ", row))


#### Plot the mean of the frequency response over several rows ####

# User enter rows of interest
row_min = 25
row_max = 30

# Select data
resp_chunk = resp <- slm_data_3oct[row_min:row_max,10:44]

# Calculate mean and standard deviation for each column
column_means <- colMeans(resp_chunk)
column_stddev <- apply(resp_chunk, 2, sd)

freq_data <- data.frame(
  frequency = freq_3oct,
  response = column_means,
  sd = as.numeric(column_stddev)
)

# Plot
ggplot(freq_data, aes(x = frequency, y = response)) +
  geom_ribbon(aes(ymin = response - sd, ymax = response + sd), alpha = 0.2) +
  geom_line(color = "blue") +
  geom_point(color = "red", size = 1) +
  geom_text(aes(label = frequency), vjust = -1, size = 3) +
  scale_x_log10() +
  labs(x = "Frequency (Hz) - Log Scale", y = "Sound Level (dB)") + 
  ggtitle("SLM frequency-response", 
          subtitle = paste("1/3 octave from 8Hz to 20000Hz for rows number: ", 
                           row_min, " - ", row_max))












