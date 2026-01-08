import serial
import time
import binascii

def test_bs205_manual():
    # Configuration
    PORT = 'COM8'
    BAUDRATE = 9600
    BYTESIZE = 8
    PARITY = serial.PARITY_EVEN  # Even parity
    STOPBITS = 1
    TIMEOUT = 1.0

    ID_INT = 0
    ID_BYTE = 0x30 + ID_INT  # 0x30 ('0')

    print(f"Opening {PORT} {BAUDRATE} 8E1...")

    try:
        ser = serial.Serial(
            port=PORT,
            baudrate=BAUDRATE,
            bytesize=BYTESIZE,
            parity=PARITY,
            stopbits=STOPBITS,
            timeout=TIMEOUT
        )

        print("Port opened successfully.")

        commands = {
            'R': ('Read Weight', 0x52), # 'R'
            'Z': ('Zero', 0x5A),        # 'Z'
            'H': ('Hold', 0x48),        # 'H'
            'L': ('Release', 0x4C)      # 'L'
        }

        while True:
            print("\nSelect command:")
            print("1. Read Weight (R)")
            print("2. Zero (Z)")
            print("3. Hold (H)")
            print("4. Release (L)")
            print("Q. Quit")

            choice = input("Enter choice: ").upper()

            if choice == 'Q':
                break

            cmd_char = None
            if choice == '1': cmd_char = 'R'
            elif choice == '2': cmd_char = 'Z'
            elif choice == '3': cmd_char = 'H'
            elif choice == '4': cmd_char = 'L'

            if cmd_char:
                desc, char_code = commands[cmd_char]

                # Construct 2-byte command
                cmd_bytes = bytes([ID_BYTE, char_code])

                print(f"\nSending {desc} command...")
                print(f"Hex to send: {binascii.hexlify(cmd_bytes).decode().upper()}")

                # Clear buffers
                ser.reset_input_buffer()
                ser.reset_output_buffer()

                # Send
                ser.write(cmd_bytes)

                # Wait a bit
                time.sleep(0.2)

                # Read response (10 bytes for Read, others might have no response or simple ack logic if device supported it, but here we just read whatever comes)
                if cmd_char == 'R':
                    response = ser.read(10)
                    if response:
                        print(f"Received ({len(response)} bytes): {binascii.hexlify(response).decode().upper()}")
                        try:
                            print(f"ASCII: {response.decode('ascii', errors='replace')}")
                        except:
                            pass
                    else:
                        print("No response received (Timeout)")
                else:
                    print("Command sent (No response expected for this command)")

    except serial.SerialException as e:
        print(f"Serial Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("\nPort closed.")

if __name__ == "__main__":
    test_bs205_manual()
