import re
from typing import List, Tuple

def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
    """
    Valida la fortaleza de una contraseña.
    
    Args:
        password: La contraseña a validar
        
    Returns:
        Tuple[bool, List[str]]: (es_válida, lista_de_errores)
    """
    errors = []
    
    # Longitud mínima
    if len(password) < 8:
        errors.append("La contraseña debe tener al menos 8 caracteres")
    
    # Debe contener al menos un número
    if not re.search(r"\d", password):
        errors.append("La contraseña debe contener al menos un número")
    
    # Debe contener al menos una letra mayúscula
    if not re.search(r"[A-Z]", password):
        errors.append("La contraseña debe contener al menos una letra mayúscula")
    
    # Debe contener al menos una letra minúscula
    if not re.search(r"[a-z]", password):
        errors.append("La contraseña debe contener al menos una letra minúscula")
    
    # Debe contener al menos un carácter especial
    if not re.search(r"[ !@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", password):
        errors.append("La contraseña debe contener al menos un carácter especial")
    
    # Verificar que no contenga palabras comunes
    common_words = ['password', 'contraseña', '123456', 'qwerty', 'admin']
    if any(word in password.lower() for word in common_words):
        errors.append("La contraseña no debe contener palabras comunes o secuencias obvias")
    
    return len(errors) == 0, errors
