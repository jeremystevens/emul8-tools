import customtkinter as ctk
from gui.rom_manager_gui import ROMManagerGUI

def main():
    # Set appearance mode to dark
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create and run the application
    app = ROMManagerGUI()
    app.run()

if __name__ == "__main__":
    main()