from tkinter import messagebox


def action_get_info_dialog():
    m_text = "\
************************\n\
Autor: Jacob Thönes\n\
Date: January 2023\n\
Version: 1.00\n\
Contct: jacob.thoenes@uni-rostock.de \n\
************************"
    messagebox.showinfo(message=m_text, title="Info")


def action_get_info_dialog_traj():
    m_text = "\
************************\n\
TBD\n\
************************"
    messagebox.showinfo(message=m_text, title="Info")


def action_get_info_dialog_kat_traj():
    m_text = "\
************************\n\
TBD\n\
************************"
    messagebox.showinfo(message=m_text, title="Info")
