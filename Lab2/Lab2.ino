// ESP32 to MPU-6050 I2C Communication (Bit-Banged)
// Using Arduino I/O abstraction

#define SCL 1
#define SDA 2

// MPU-6050 I2C address
#define MPU6050_ADDR 0x68

// MPU-6050 Register addresses
#define REG_ACCEL_XOUT_H 0x3B
#define REG_ACCEL_XOUT_L 0x3C
#define REG_ACCEL_YOUT_H 0x3D
#define REG_ACCEL_YOUT_L 0x3E
#define REG_ACCEL_ZOUT_H 0x3F
#define REG_ACCEL_ZOUT_L 0x40
#define REG_PWR_MGMT_1   0x6B

// I2C timing (microseconds)
#define I2C_DELAY 10  // For ~50KHz operation (well under 400KHz max)

// ==================== I2C Low-Level Functions ====================
// Initialize both I2C pins as open-drain outputs, high (idle)
void i2c_init() {
  pinMode(SCL, OUTPUT_OPEN_DRAIN);
  pinMode(SDA, OUTPUT_OPEN_DRAIN);
  digitalWrite(SCL, HIGH);
  digitalWrite(SDA, HIGH);
  delayMicroseconds(I2C_DELAY);
}

// Initialize start condition (SDA goes LOW while SCL is HIGH)
void i2c_start() {
  pinMode(SDA, OUTPUT_OPEN_DRAIN);  // Ensure SDA is set to output mode
  digitalWrite(SDA, HIGH); // Ensure SDA is high before starting
  delayMicroseconds(I2C_DELAY); // Short delay to ensure bus is idle
  digitalWrite(SCL, HIGH); // Ensure SCL is high before starting
  delayMicroseconds(I2C_DELAY); // Short delay to ensure bus is idle
  digitalWrite(SDA, LOW); // Start condition: SDA goes LOW while SCL is HIGH
  delayMicroseconds(I2C_DELAY); // Short delay to ensure the start condition is recognized
  digitalWrite(SCL, LOW); // Pull SCL low to prepare for data transmission
  delayMicroseconds(I2C_DELAY); // Short delay to ensure the bus is ready for data transmission
}

// Initialize stop condition (SDA goes HIGH while SCL is HIGH)
void i2c_stop() {
  pinMode(SDA, OUTPUT_OPEN_DRAIN); // Ensure SDA is set to output mode
  digitalWrite(SDA, LOW); // Ensure SDA is low before stopping
  delayMicroseconds(I2C_DELAY); // Short delay to ensure the bus is ready for stop condition
  digitalWrite(SCL, HIGH); // Ensure SCL is high before stopping
  delayMicroseconds(I2C_DELAY); // Short delay to ensure the stop condition is recognized
  digitalWrite(SDA, HIGH); // Stop condition: SDA goes HIGH while SCL is HIGH
  delayMicroseconds(I2C_DELAY); // Short delay to ensure the stop condition is recognized
}

// Pulse the SCL line for one clock cycle
void i2c_pulse_clock() {
  digitalWrite(SCL, HIGH); // Clock goes HIGH
  delayMicroseconds(I2C_DELAY); // Short delay to ensure the clock pulse is recognized
  digitalWrite(SCL, LOW); // Clock goes LOW
  delayMicroseconds(I2C_DELAY); // Short delay to ensure the clock pulse is complete
}

// Write a byte to the I2C bus and read ACK/NACK
bool i2c_write_byte(uint8_t data) {
  // Send 8 bits, MSB first
  pinMode(SDA, OUTPUT_OPEN_DRAIN);
  
  for (int i = 7; i >= 0; i--) {
    // Set SDA to the bit value
    if (data & (1 << i)) {
      digitalWrite(SDA, HIGH);
    } else {
      digitalWrite(SDA, LOW);
    }
    delayMicroseconds(I2C_DELAY);
    
    // Pulse the clock
    i2c_pulse_clock();
  }
  
  // Release SDA and read ACK (9th clock cycle)
  pinMode(SDA, INPUT_PULLUP);
  delayMicroseconds(I2C_DELAY);
  
  digitalWrite(SCL, HIGH);
  delayMicroseconds(I2C_DELAY);
  
  // Read ACK bit (LOW = ACK, HIGH = NACK)
  bool ack = (digitalRead(SDA) == LOW);
  
  digitalWrite(SCL, LOW);
  delayMicroseconds(I2C_DELAY);
  
  return ack;  // Return true if ACK received
}

uint8_t i2c_read_byte(bool send_ack) {
  uint8_t data = 0;
  
  // Set SDA as input to receive data
  pinMode(SDA, INPUT_PULLUP);
  delayMicroseconds(I2C_DELAY);
  
  // Read 8 bits, MSB first
  for (int i = 7; i >= 0; i--) {
    digitalWrite(SCL, HIGH);
    delayMicroseconds(I2C_DELAY);
    
    if (digitalRead(SDA)) {
      data |= (1 << i);
    }
    
    digitalWrite(SCL, LOW);
    delayMicroseconds(I2C_DELAY);
  }
  
  // Send ACK or NACK (9th clock cycle)
  pinMode(SDA, OUTPUT_OPEN_DRAIN);
  if (send_ack) {
    digitalWrite(SDA, LOW);   // ACK
  } else {
    digitalWrite(SDA, HIGH);  // NACK
  }
  delayMicroseconds(I2C_DELAY);
  
  i2c_pulse_clock();
  
  return data;
}

// ==================== MPU-6050 Communication Functions ====================
bool mpu_write_register(uint8_t reg_addr, uint8_t data) {
  // Write to a single register on the MPU-6050
  // Transaction: START -> ADDR+W -> REG -> DATA -> STOP
  
  i2c_start();
  
  // Send device address with write bit (0)
  if (!i2c_write_byte(MPU6050_ADDR << 1)) {
    Serial.println("No ACK on address (write)");
    i2c_stop();
    return false;
  }
  
  // Send register address
  if (!i2c_write_byte(reg_addr)) {
    Serial.println("No ACK on register address");
    i2c_stop();
    return false;
  }
  
  // Send data
  if (!i2c_write_byte(data)) {
    Serial.println("No ACK on data");
    i2c_stop();
    return false;
  }
  
  i2c_stop();
  return true;
}

bool mpu_read_register(uint8_t reg_addr, uint8_t *data) {
  // Read a single register from the MPU-6050
  // Transaction 1: START -> ADDR+W -> REG -> STOP
  // Transaction 2: START -> ADDR+R -> DATA -> NACK -> STOP
  
  // Transaction 1: Set register address
  i2c_start();
  
  // Send device address with write bit (0)
  if (!i2c_write_byte(MPU6050_ADDR << 1)) {
    Serial.println("No ACK on address (write phase)");
    i2c_stop();
    return false;
  }
  
  // Send register address
  if (!i2c_write_byte(reg_addr)) {
    Serial.println("No ACK on register address");
    i2c_stop();
    return false;
  }
  
  // Transaction 2: Read data
  i2c_start();  // Repeated start
  
  // Send device address with read bit (1)
  if (!i2c_write_byte((MPU6050_ADDR << 1) | 1)) {
    Serial.println("No ACK on address (read phase)");
    i2c_stop();
    return false;
  }
  
  // Read data byte with NACK (last byte)
  *data = i2c_read_byte(false);
  
  i2c_stop();
  return true;
}

bool mpu_read_registers(uint8_t start_reg, uint8_t *buffer, uint8_t length) {
  // Read multiple consecutive registers from the MPU-6050
  // Transaction 1: START -> ADDR+W -> REG -> (repeated start)
  // Transaction 2: ADDR+R -> DATA1 (ACK) -> DATA2 (ACK) -> ... -> DATAn (NACK) -> STOP
  
  if (length == 0) return false;
  
  // Transaction 1: Set starting register address
  i2c_start();
  
  // Send device address with write bit (0)
  if (!i2c_write_byte(MPU6050_ADDR << 1)) {
    Serial.println("No ACK on address (write phase)");
    i2c_stop();
    return false;
  }
  
  // Send starting register address
  if (!i2c_write_byte(start_reg)) {
    Serial.println("No ACK on register address");
    i2c_stop();
    return false;
  }
  
  // Transaction 2: Read data
  i2c_start();  // Repeated start
  
  // Send device address with read bit (1)
  if (!i2c_write_byte((MPU6050_ADDR << 1) | 1)) {
    Serial.println("No ACK on address (read phase)");
    i2c_stop();
    return false;
  }
  
  // Read all bytes, ACK all except the last one
  for (uint8_t i = 0; i < length; i++) {
    bool send_ack = (i < length - 1);  // ACK for all but last byte
    buffer[i] = i2c_read_byte(send_ack);
  }
  
  i2c_stop();
  return true;
}

// ==================== MPU-6050 High-Level Functions ====================

bool mpu_init() {
  // Wake up MPU-6050 by writing 0 to power management register
  // This clears the SLEEP bit (bit 6) and sets clock to internal 8MHz
  Serial.println("Initializing MPU-6050...");
  
  if (!mpu_write_register(REG_PWR_MGMT_1, 0x00)) {
    Serial.println("Failed to initialize MPU-6050!");
    return false;
  }
  
  delay(100);  // Wait for sensor to stabilize
  
  // Verify by reading back the register
  uint8_t pwr_mgmt;
  if (!mpu_read_register(REG_PWR_MGMT_1, &pwr_mgmt)) {
    Serial.println("Failed to verify MPU-6050 initialization!");
    return false;
  }
  
  Serial.print("PWR_MGMT_1 register: 0x");
  Serial.println(pwr_mgmt, HEX);
  
  return true;
}

bool mpu_read_accel(int16_t *ax, int16_t *ay, int16_t *az) {
  // Read all 6 accelerometer registers (X, Y, Z - high and low bytes)
  uint8_t buffer[6];
  
  if (!mpu_read_registers(REG_ACCEL_XOUT_H, buffer, 6)) {
    return false;
  }
  
  // Combine high and low bytes (big-endian format)
  *ax = (int16_t)((buffer[0] << 8) | buffer[1]);
  *ay = (int16_t)((buffer[2] << 8) | buffer[3]);
  *az = (int16_t)((buffer[4] << 8) | buffer[5]);
  
  return true;
}

// ==================== Main Program ====================

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println();
  Serial.println("========================================");
  Serial.println("ESP32 to MPU-6050 I2C Communication");
  Serial.println("Using Bit-Banged I2C Protocol");
  Serial.println("========================================");
  Serial.println();
  
  // Initialize I2C pins
  i2c_init();
  Serial.println("I2C initialized on SCL=1, SDA=2");
  
  // Initialize MPU-6050
  if (!mpu_init()) {
    Serial.println("MPU-6050 initialization failed!");
    Serial.println("Check wiring and connections.");
    while (1) {
      delay(1000);
    }
  }
  
  Serial.println("MPU-6050 initialized successfully!");
  Serial.println();
  Serial.println("Reading accelerometer data...");
  Serial.println();
}

void loop() {
  int16_t ax, ay, az;
  
  if (mpu_read_accel(&ax, &ay, &az)) {
    // Print raw values
    Serial.print("Accel X: ");
    Serial.print(ax);
    Serial.print(" | Y: ");
    Serial.print(ay);
    Serial.print(" | Z: ");
    Serial.print(az);
    
    // Convert to g's (default range is +/- 2g, 16384 LSB/g)
    float ax_g = ax / 16384.0;
    float ay_g = ay / 16384.0;
    float az_g = az / 16384.0;
    
    Serial.print(" || g: X=");
    Serial.print(ax_g, 2);
    Serial.print(" Y=");
    Serial.print(ay_g, 2);
    Serial.print(" Z=");
    Serial.println(az_g, 2);
  } else {
    Serial.println("Failed to read accelerometer data!");
  }
  
  delay(500);  // Read at 2Hz for readability
}
