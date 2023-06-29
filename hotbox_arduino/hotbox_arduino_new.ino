// VADL Hotbox Arduino Code for Arduino Nano
// Cameron Schepner, cameron.j.schepner@vanderbilt.edu
// 6/16/2021

#define relayPin 7 // SS relay pin
#define r1 A0 //thermistor 1
#define r2 A1 //thermistor 2
#define r3 A2 //thermistor 3
#define r4 A3 //thermistor 4

const int period = 10;          //period for moving average, s
float rVals[4];
float tVals[4];
const float volt_div_res1 = 13330; //measured resistance of resistor 1 in voltage divider
const float volt_div_res2 = 13260; //measured resistance of resistor 2 in voltage divider
const float volt_div_res3 = 13300; //measured resistance of resistor 3 in voltage divider
const float volt_div_res4 = 14000; //measured resistance of resistor 4 in voltage divider
const float chip_bit = 1024;      //max bit value of microcontroller (10-bit in this case)

// constants obtained from experimental data (calibration)
// used in the Steinhart-Hart thermistor equations to get temp from resistance

const float r1_const[3] = {0.001162980253257, 0.000236900291397, 0.000000051966197};
const float r2_const[3] = {0.001275745803910, 0.000215513547371, 0.000000150379108};
const float r3_const[3] = {0.001303318607580, 0.000212997273502, 0.000000166121389};
const float r4_const[3] = {0.001475178372924, 0.000174424909919, 0.000000376627988};
                                //arrays above are constants derived from experimental
                                //data for each thermistor

//////   USER INPUT HERE    //////////////////////////   USER INPUT HERE   ////////////////////////

const float T_set = 118;          //input your favorite temp here in F
const float t_buff = 1.5;           //buffer size for control loop 
                                //1.5 deg is fine
                                
///////////////////////////////////////////////////////////////////////////////////////////////////
                                
void setup() {
  Serial.begin(9600);
  Serial.println("VADL Hotbox Operation \n \n");
  Serial.println("Beep boop beep, calibrating... \n \n");
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, HIGH);
}

void loop() {
  
  float t_sum = 0;
  for (int i = 0; i < period*100; i++) { //get average temp over 'period' seconds
    getTVals();
    float avg_T_mat = (tVals[0] + tVals[1] + tVals[2] + tVals[3]) / 4;
    t_sum += avg_T_mat;
    delay(10);
  }
  float T_avg = t_sum/(period*100); //average temp over 'period' s
  
  if ( T_avg < (T_set) && !isnan(T_avg) ) {
    digitalWrite(relayPin, HIGH);
    Serial.print("Average Temperature = ");
    Serial.println(T_avg);
    Serial.println("\nToo COLD \n");
  }
  else if ( T_avg > (T_set + t_buff) ) {
    digitalWrite(relayPin, LOW);
    Serial.print("Average Temperature = ");
    Serial.println(T_avg);
    Serial.println("\nToo HOT \n");
  }
  else if ( isnan(T_avg) ) {
    digitalWrite(relayPin, LOW);
    Serial.print("Uh oh spaghettio, something went wrong (check connections)");
    Serial.println();
  }
  else {
    digitalWrite(relayPin, LOW);
    Serial.print("Average Temperature = ");
    Serial.println(T_avg);
    Serial.println("\nJust Riiiight \n");
  }

  getTVals();
    Serial.println("Current Individual Thermistor Readings: \n");
    printArray( tVals, sizeof(tVals)/sizeof(tVals[0]) );
    Serial.println("\n \n");
  
}


void getTVals() { //calculate the temp recorded by each thermistor in F
  
  getRVals();
  
  //if u need to check resistance values of thermistors uncomment this line
  //printArray(rVals,4);

  tVals[0] = 32 + 1.8 * (1 / (r1_const[0] + r1_const[1]*log(rVals[0]) + r1_const[2]*pow(log(rVals[0]),3)) - 273.15);
  tVals[1] = 32 + 1.8 * (1 / (r2_const[0] + r2_const[1]*log(rVals[1]) + r2_const[2]*pow(log(rVals[1]),3)) - 273.15);
  tVals[2] = 32 + 1.8 * (1 / (r3_const[0] + r3_const[1]*log(rVals[2]) + r3_const[2]*pow(log(rVals[2]),3)) - 273.15);
  tVals[3] = 32 + 1.8 * (1 / (r4_const[0] + r4_const[1]*log(rVals[3]) + r4_const[2]*pow(log(rVals[3]),3)) - 273.15);
}

void getRVals() { //retrieve analog input values and convert to resistance
  rVals[0] = volt_div_res1 / (chip_bit/(analogRead(r1) - 1));
  rVals[1] = volt_div_res2 / (chip_bit/(analogRead(r2) - 1));
  rVals[2] = volt_div_res3 / (chip_bit/(analogRead(r3) - 1));
  rVals[3] = volt_div_res4 / (chip_bit/(analogRead(r4) - 1));
}

void printArray(float *arrayContents, int arrayLength) { //print contents of any array to serial
  for (int i = 0; i < arrayLength; i++) {
    Serial.print(arrayContents[i]);
    Serial.print('\t');
  }
  Serial.println();
}
