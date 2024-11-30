# AARDEMScheduler

Este es un sistema desarrollado en Python con Flask para gestionar horarios de clases de música, permitiendo agregar profesores, clases y excepciones. El sistema sincroniza automáticamente los datos con Google Sheets para mantener un registro actualizado.

---

## **Características**
- Gestión de horarios por maestro.
- Soporte para clases regulares y excepciones. (clases de prueba y reposiciones)
- Sincronización automática con Google Sheets.
- Interfaz web amigable.

---

## **Requisitos**
1. **Python 3.9 o superior**
2. Flask
3. Gspread
4. oauth2client
5. Credenciales para conectar a google sheets. (Se explica más tarde)

## **Instalación**
1. **Clona el repositorio.**
```bash
git clone https://github.com/zekar47/AARDEMScheduler/
```

2. **Crea y activa un entorno virtual.**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Instala las dependencias.**
```bash
pip install flask gspread oauth2client
```

4. **Configura las credenciales de Google Sheets**:
   - Descarga tus credenciales desde Google Cloud Platform.
   - Guarda el archivo `credentials.json` en el directorio raíz del proyecto.

5. **Ejecuta la aplicación**:
   ```bash
   python app.py
   ```

6. **Abre la aplicación en tu navegador**:
   - La aplicación estará disponible en: [http://127.0.0.1:5000](http://127.0.0.1:5000).

## **Uso**
### **Agregar un maestro.**
1. Asegúrate de tener un documento en Google Sheets preparado.
2. Ve a la página "Agregar Maestro".
3. Ingresa la información requerida.
![image](https://github.com/user-attachments/assets/370ea398-f2e8-481b-bd54-d457e1debc04)

### **Agregar una clase.**
1. Ve a la página "Agregar Clase".
2. Ingresa la información requerida.
3. Guarda la información.
4. Automaticamente debería agregarse al documento en Google Sheets.
![image](https://github.com/user-attachments/assets/49265300-7ee4-474e-a82e-25c834c912c3)


### **Estado de clase.**
1. Ve a la página "Estado de Clase".
2. Elige un maestro de la lista.
3. Ingresa la información requerida.
4. El nombre del alumno se deducirá automaticamente dado el horario de la clase
5. Agrega notas (opcionales).
![image](https://github.com/user-attachments/assets/e85174a9-da9e-44dd-90a9-5f818cfb7137)
