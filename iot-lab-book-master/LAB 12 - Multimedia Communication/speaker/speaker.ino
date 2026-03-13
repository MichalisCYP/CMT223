/****************************************************************************
 * File Name: Grove_Speaker_Example
 *
 * Updated Version: 25/12/2024 (by Charith PERERA)
 *
 * Purpose:
 *   - Demonstrates generating different musical notes using a Grove Speaker.
 *   - Cycles through bass notes (1 through 7) and plays each for one second.
 *   - Can be extended to create melodies or to provide audio feedback in IoT
 *     applications (e.g., alerts, notifications, etc.).
 *
 * Reference:
 *   - https://wiki.seeedstudio.com/Grove-Speaker/
 ****************************************************************************/



/* 1. Macro definition of the Speaker pin on the Grove board. */
#define SPEAKER 4

// 2. An array of tone frequencies (in microseconds) for bass notes 1 through 7.
//    Each value in BassTab corresponds to one musical note frequency. 
int BassTab[] = {1911, 1702, 1516, 1431, 1275, 1136, 1012};

// ---------------------------------------------------------------------------
// SETUP
// ---------------------------------------------------------------------------
void setup()
{
    pinInit();  // Initialize the speaker pin.
}

// ---------------------------------------------------------------------------
// LOOP
// ---------------------------------------------------------------------------
void loop()
{
    // 3. Sequentially play bass notes 1 to 7 (based on the BassTab array).
    //    Each note is played for 1 second (1000 ms).
    for(int note_index = 0; note_index < 7; note_index++)
    {
        sound(note_index);
        delay(1000);  // Wait 1 second before playing the next note.
    }
}

// ---------------------------------------------------------------------------
// PIN INITIALIZATION
// ---------------------------------------------------------------------------
void pinInit()
{
    // 4. Configure the speaker pin as an OUTPUT and set it LOW to start.
    pinMode(SPEAKER, OUTPUT);
    digitalWrite(SPEAKER, LOW);
}

// ---------------------------------------------------------------------------
// SOUND FUNCTION
// ---------------------------------------------------------------------------
/**
 * Function: sound
 * ---------------
 * @param note_index: Index corresponding to one of the bass notes in BassTab
 *
 * This function generates a tone on the speaker by toggling the SPEAKER pin
 * at the frequency specified in the BassTab array.
 * 
 * - Each note is played for 100 cycles.
 * - The duration of each HIGH and LOW state is determined by BassTab[note_index].
 */
void sound(uint8_t note_index)
{
    for(int i = 0; i < 100; i++)
    {
        // Turn the speaker ON (HIGH).
        digitalWrite(SPEAKER, HIGH);
        // Wait a period defined by the bass note frequency in microseconds.
        delayMicroseconds(BassTab[note_index]);

        // Turn the speaker OFF (LOW).
        digitalWrite(SPEAKER, LOW);
        // Wait the same period to complete the cycle of one "square wave."
        delayMicroseconds(BassTab[note_index]);
    }
}

