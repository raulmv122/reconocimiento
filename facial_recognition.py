from tkinter import *
from tkinter import messagebox as msg
import os
import cv2
from matplotlib import pyplot as plt
from mtcnn.mtcnn import MTCNN
import database as db

# CONFIGURACIÓN
ruta = "C:/Users/raulm/Documents/GitHub/reconocimiento/"
txt_login = "Iniciar Sesión"
txt_register = "Registrarse"

color_blanco = "#f4f5f4"
color_negro = "#101010"

color_btn_negro = "#202020"
color_fondo = "#151515"

fuente_label = "Century Gothic"
tamano_pantalla = "500x300"

# Colores
exito = "\033[1;32;40m"
error = "\033[1;31;40m"
normal = "\033[0;37;40m"

res_bd = {"id": 0, "afectados": 0}  # variable de base de datos

# GENERAL
def presionar_enter(pantalla):
    ''' Añade un salto de línea en la pantalla '''
    Label(pantalla, text="", bg=color_fondo).pack()

def imprimir_y_mostrar(pantalla, texto, bandera):
    ''' Imprime y muestra el texto '''
    if bandera:
        print(exito + texto + normal)
        pantalla.destroy()
        msg.showinfo(message=texto, title="¡Éxito!")
    else:
        print(error + texto + normal)
        Label(pantalla, text=texto, fg="red", bg=color_fondo, font=(fuente_label, 12)).pack()

def configurar_pantalla(pantalla, texto):
    ''' Configura los estilos globales '''
    pantalla.title(texto)
    pantalla.geometry(tamano_pantalla)
    pantalla.configure(bg=color_fondo)
    Label(pantalla, text=f"¡{texto}!", fg=color_blanco, bg=color_negro, font=(fuente_label, 18), width="500", height="2").pack()

def credenciales(pantalla, variable, bandera):
    ''' Configuración de la entrada del usuario '''
    Label(pantalla, text="Usuario:", fg=color_blanco, bg=color_fondo, font=(fuente_label, 12)).pack()
    entrada = Entry(pantalla, textvariable=variable, justify=CENTER, font=(fuente_label, 12))
    entrada.focus_force()
    entrada.pack(side=TOP, ipadx=30, ipady=6)

    presionar_enter(pantalla)
    if bandera:
        Button(pantalla, text="Capturar rostro", fg=color_blanco, bg=color_btn_negro, activebackground=color_fondo, borderwidth=0, font=(fuente_label, 14), height="2", width="40", command=capturar_login).pack()
    else:
        Button(pantalla, text="Capturar rostro", fg=color_blanco, bg=color_btn_negro, activebackground=color_fondo, borderwidth=0, font=(fuente_label, 14), height="2", width="40", command=capturar_registro).pack()
    return entrada

def mostrar_rostro(img, rostros):
    data = plt.imread(img)
    for i in range(len(rostros)):
        x1, y1, ancho, alto = rostros[i]["box"]
        x2, y2 = x1 + ancho, y1 + alto
        plt.subplot(1, len(rostros), i + 1)
        plt.axis("off")
        rostro = cv2.resize(data[y1:y2, x1:x2], (150, 200), interpolation=cv2.INTER_CUBIC)
        cv2.imwrite(img, rostro)
        plt.imshow(data[y1:y2, x1:x2])

# REGISTRO #
def registrar_en_bd(img):
    nombre_usuario = img.replace(".jpg", "").replace(".png", "")
    res_bd = db.registrarUsuario(nombre_usuario, ruta + img)

    presionar_enter(pantalla1)
    if res_bd["afectados"]:
        imprimir_y_mostrar(pantalla1, "¡Éxito! Se ha registrado correctamente", 1)
    else:
        imprimir_y_mostrar(pantalla1, "¡Error! No se ha registrado correctamente", 0)
    os.remove(img)

def capturar_registro():
    cap = cv2.VideoCapture(0)
    usuario_reg = usuario1.get()
    img = f"{usuario_reg}.jpg"

    while True:
        ret, frame = cap.read()
        cv2.imshow("Captura Facial", frame)
        if cv2.waitKey(1) == 27:
            break

    cv2.imwrite(img, frame)
    cap.release()
    cv2.destroyAllWindows()

    entrada_usuario1.delete(0, END)

    pixels = plt.imread(img)
    rostros = MTCNN().detect_faces(pixels)
    mostrar_rostro(img, rostros)
    registrar_en_bd(img)

def registrar():
    global usuario1
    global entrada_usuario1
    global pantalla1

    pantalla1 = Toplevel(root)
    usuario1 = StringVar()

    configurar_pantalla(pantalla1, txt_register)
    entrada_usuario1 = credenciales(pantalla1, usuario1, 0)

# INICIO DE SESIÓN #
def compatibilidad(img1, img2):
    orb = cv2.ORB_create()

    puntos_clave1, des1 = orb.detectAndCompute(img1, None)
    puntos_clave2, des2 = orb.detectAndCompute(img2, None)

    comparador = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    coincidencias = comparador.match(des1, des2)

    similares = [x for x in coincidencias if x.distance < 70]
    if len(coincidencias) == 0:
        return 0
    return len(similares) / len(coincidencias)

def capturar_login():
    cap = cv2.VideoCapture(0)
    usuario_ingreso = usuario2.get()
    img = f"{usuario_ingreso}_login.jpg"
    img_usuario = f"{usuario_ingreso}.jpg"

    while True:
        ret, frame = cap.read()
        cv2.imshow("Ingreso Facial", frame)
        if cv2.waitKey(1) == 27:
            break

    cv2.imwrite(img, frame)
    cap.release()
    cv2.destroyAllWindows()

    entrada_usuario2.delete(0, END)

    pixels = plt.imread(img)
    rostros = MTCNN().detect_faces(pixels)

    mostrar_rostro(img, rostros)
    presionar_enter(pantalla2)

    res_bd = db.obtenerUsuario(usuario_ingreso, ruta + img_usuario)
    if res_bd["afectados"]:
        mis_archivos = os.listdir()
        if img_usuario in mis_archivos:
            rostro_reg = cv2.imread(img_usuario, 0)
            rostro_log = cv2.imread(img, 0)

            compat = compatibilidad(rostro_reg, rostro_log)

            if compat >= 0.94:
                print("{}Compatibilidad del {:.1%}{}".format(exito, float(compat), normal))
                imprimir_y_mostrar(pantalla2, f"Bienvenido(a), {usuario_ingreso}", 1)
            else:
                print("{}Compatibilidad del {:.1%}{}".format(error, float(compat), normal))
                imprimir_y_mostrar(pantalla2, "¡Error! Incompatibilidad de datos", 0)
            os.remove(img_usuario)

        else:
            imprimir_y_mostrar(pantalla2, "¡Error! Usuario no encontrado", 0)
    else:
        imprimir_y_mostrar(pantalla2, "¡Error! Usuario no encontrado", 0)
    os.remove(img)

def iniciar_sesion():
    global pantalla2
    global usuario2
    global entrada_usuario2

    pantalla2 = Toplevel(root)
    usuario2 = StringVar()

    configurar_pantalla(pantalla2, txt_login)
    entrada_usuario2 = credenciales(pantalla2, usuario2, 1)

root = Tk()
root.geometry(tamano_pantalla)
root.title("AVM")
root.configure(bg=color_fondo)
Label(text="¡Bienvenido(a)!", fg=color_blanco, bg=color_negro, font=(fuente_label, 18), width="500", height="2").pack()

presionar_enter(root)
Button(text=txt_login, fg=color_blanco, bg=color_btn_negro, activebackground=color_fondo, borderwidth=0, font=(fuente_label, 14), height="2", width="40", command=iniciar_sesion).pack()

presionar_enter(root)
Button(text=txt_register, fg=color_blanco, bg=color_btn_negro, activebackground=color_fondo, borderwidth=0, font=(fuente_label, 14), height="2", width="40", command=registrar).pack()

root.mainloop()
